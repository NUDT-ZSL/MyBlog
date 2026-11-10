"""Markdown rendering tuned for a technical Chinese blog.

Features:
* Pygments-highlighted fenced code with language labels, line numbers and a
  copy button (the button is wired up in static/js/main.js).
* Mermaid diagrams left as data for the client-side renderer.
* KaTeX-friendly math placeholders that survive Markdown's escaping rules.
* Obsidian-style ``[[wiki links]]`` resolved against the note index.
* A flattened table of contents built from Markdown's toc extension.
"""
from __future__ import annotations

import html
import re
from dataclasses import dataclass, field
from typing import Any

import markdown
from django.utils.text import slugify
from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor
from markdown.preprocessors import Preprocessor
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import TextLexer, get_lexer_by_name
from pygments.util import ClassNotFound
from xml.etree import ElementTree as etree

LANGUAGE_ALIASES = {
    "c++": "cpp",
    "cc": "cpp",
    "h": "cpp",
    "hpp": "cpp",
    "py": "python",
    "sh": "bash",
    "shell": "bash",
    "zsh": "bash",
    "console": "bash",
    "ll": "llvm",
    "ir": "llvm",
    "llvm-ir": "llvm",
    "sv": "verilog",
    "systemverilog": "verilog",
    "v": "verilog",
    "js": "javascript",
    "ts": "typescript",
    "yml": "yaml",
    "md": "markdown",
    "txt": "text",
    "plaintext": "text",
}

LANGUAGE_LABELS = {
    "cpp": "C++",
    "python": "Python",
    "verilog": "Verilog",
    "llvm": "LLVM IR",
    "bash": "Shell",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "json": "JSON",
    "yaml": "YAML",
    "html": "HTML",
    "css": "CSS",
    "sql": "SQL",
    "makefile": "Makefile",
    "cmake": "CMake",
    "text": "TEXT",
    "markdown": "Markdown",
    "mermaid": "Mermaid",
}

WIKI_PATTERN = r"\[\[([^\[\]|]+?)(?:\|([^\[\]]+?))?\]\]"
WIKI_RE = re.compile(WIKI_PATTERN)


@dataclass
class TocItem:
    level: int
    name: str
    id: str


@dataclass
class RenderedContent:
    html: str
    toc: list[TocItem] = field(default_factory=list)
    unresolved_links: int = 0


def normalize_link_key(value: str) -> str:
    return re.sub(r"\s+", "", value).strip().casefold()


def _render_code_block(code: str, language: str) -> str:
    lang = LANGUAGE_ALIASES.get(language.lower(), language.lower() or "text")
    label = LANGUAGE_LABELS.get(lang, lang.upper() or "TEXT")
    if lang == "mermaid":
        return (
            '<figure class="diagram-block">'
            '<figcaption><span class="diagram-label">MERMAID</span>'
            '<span class="diagram-hint">渲染为图</span></figcaption>'
            f'<div class="mermaid">{html.escape(code)}</div>'
            "</figure>"
        )

    try:
        lexer = get_lexer_by_name(lang, stripall=False, ensurenl=False)
    except ClassNotFound:
        lexer = TextLexer(stripall=False)
        label = label if language else "TEXT"

    formatter = HtmlFormatter(
        cssclass="highlight",
        linenos="inline",
        linenostart=1,
        nowrap=False,
        wrapcode=True,
    )
    highlighted = highlight(code, lexer, formatter)
    safe_lang = re.sub(r"[^a-z0-9_-]", "", lang) or "text"
    return (
        f'<figure class="code-block" data-lang="{safe_lang}">'
        '<figcaption class="code-caption">'
        f'<span class="code-dots" aria-hidden="true"><i></i><i></i><i></i></span>'
        f'<span class="code-lang">{html.escape(label)}</span>'
        '<button class="code-copy" type="button" aria-label="复制代码">'
        '<svg class="icon" aria-hidden="true"><use href="#icon-copy"></use></svg>'
        "<span>复制</span></button>"
        "</figcaption>"
        f"{highlighted}"
        "</figure>"
    )


class CodeFencePreprocessor(Preprocessor):
    """Render fenced code blocks ourselves so the markup is consistent."""

    RE = re.compile(r"^```([A-Za-z0-9_+#.\-]*)[ \t]*\n(.*?)^```[ \t]*$", re.MULTILINE | re.DOTALL)

    def run(self, lines):
        text = "\n".join(lines)

        def replace(match):
            lang = (match.group(1) or "").strip().lower()
            code = match.group(2).rstrip("\n")
            block = _render_code_block(code, lang)
            placeholder = self.md.htmlStash.store(block)
            return f"\n\n{placeholder}\n\n"

        text = self.RE.sub(replace, text)
        return text.split("\n")


class MathPreprocessor(Preprocessor):
    """Protect TeX before inline emphasis and underscores get a chance to eat it."""

    DISPLAY_RE = re.compile(r"\$\$(.+?)\$\$", re.DOTALL)
    INLINE_RE = re.compile(r"(?<!\\)\$(?![\s$])([^\n$]+?)(?<![\s\\])\$(?![\d$])")

    def run(self, lines):
        text = "\n".join(lines)

        def display(match):
            block = (
                '<div class="math-display" role="math">'
                f"\\[{html.escape(match.group(1).strip())}\\]"
                "</div>"
            )
            return f"\n\n{self.md.htmlStash.store(block)}\n\n"

        def inline(match):
            block = (
                '<span class="math-inline" role="math">'
                f"\\({html.escape(match.group(1))}\\)"
                "</span>"
            )
            return self.md.htmlStash.store(block)

        text = self.DISPLAY_RE.sub(display, text)
        text = self.INLINE_RE.sub(inline, text)
        return text.split("\n")


class WikiLinkInlineProcessor(InlineProcessor):
    def __init__(self, pattern, md, links, counter):
        super().__init__(pattern, md)
        self.links = links
        self.counter = counter

    def handleMatch(self, m, data):
        raw = m.group(1).strip()
        label = (m.group(2) or raw).strip()
        target_part, _, anchor_part = raw.partition("#")
        target = self.links.get(normalize_link_key(target_part))
        if target:
            anchor = f"#{slugify(anchor_part, allow_unicode=True)}" if anchor_part else ""
            el = etree.Element("a")
            el.set("href", target + anchor)
            el.set("class", "wiki-link")
            el.set("title", f"跳转到笔记：{raw}")
            el.text = label
        else:
            self.counter["unresolved"] += 1
            el = etree.Element("span")
            el.set("class", "wiki-link is-missing")
            el.set("title", f"尚未创建：{raw}")
            el.text = label
        return el, m.start(0), m.end(0)


class BlogMarkdownExtension(Extension):
    def __init__(self, note_links=None, **kwargs):
        self.note_links = note_links or {}
        self.counter = {"unresolved": 0}
        super().__init__(**kwargs)

    def extendMarkdown(self, md):
        md.preprocessors.register(CodeFencePreprocessor(md), "ir_code_fence", 28)
        md.preprocessors.register(MathPreprocessor(md), "ir_math", 27)
        md.inlinePatterns.register(
            WikiLinkInlineProcessor(WIKI_PATTERN, md, self.note_links, self.counter),
            "ir_wikilink",
            85,
        )


def _flatten_toc(tokens: list[dict[str, Any]], items: list[TocItem] | None = None) -> list[TocItem]:
    if items is None:
        items = []
    for token in tokens:
        if token.get("level", 0) <= 3:
            items.append(
                TocItem(
                    level=int(token.get("level", 2)),
                    name=re.sub(r"<[^>]+>", "", token.get("name", "")),
                    id=token.get("id", ""),
                )
            )
        children = token.get("children") or []
        if children:
            _flatten_toc(children, items)
    return items


def render_markdown(text: str, note_links: dict[str, str] | None = None) -> RenderedContent:
    extension = BlogMarkdownExtension(note_links=note_links)
    md = markdown.Markdown(
        extensions=[
            "abbr",
            "attr_list",
            "def_list",
            "footnotes",
            "md_in_html",
            "sane_lists",
            "tables",
            "toc",
            extension,
        ],
        extension_configs={
            "toc": {
                "toc_depth": "2-3",
                "permalink": False,
                "slugify": lambda value, separator: slugify(value, allow_unicode=True),
            },
            "footnotes": {"UNIQUE_IDS": True},
        },
        output_format="html5",
    )
    rendered = md.convert(text)
    toc = _flatten_toc(getattr(md, "toc_tokens", []))
    return RenderedContent(html=rendered, toc=toc, unresolved_links=extension.counter["unresolved"])


def extract_wiki_targets(text: str) -> set[str]:
    return {normalize_link_key(match.group(1).partition("#")[0]) for match in WIKI_RE.finditer(text)}
