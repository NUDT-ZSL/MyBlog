/* IR 之下 — interactions. Small, dependency-free, progressively enhanced. */
(function () {
  "use strict";

  const $ = (selector, scope = document) => scope.querySelector(selector);
  const $$ = (selector, scope = document) => Array.from(scope.querySelectorAll(selector));
  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ------------------------------------------------------------------------
     Theme
     ------------------------------------------------------------------------ */

  function currentTheme() {
    return document.documentElement.getAttribute("data-theme") || "dark";
  }

  function setTheme(theme, persist = true) {
    document.documentElement.setAttribute("data-theme", theme);
    document.documentElement.style.colorScheme = theme;
    if (persist) {
      try {
        localStorage.setItem("ir-theme", theme);
      } catch (error) {
        /* private mode: theme still applies for this page */
      }
    }
    const meta = $('meta[name="theme-color"]');
    if (meta) meta.setAttribute("content", theme === "light" ? "#f4f2ec" : "#090e13");
    const toggle = $("[data-theme-toggle]");
    if (toggle) {
      toggle.setAttribute("aria-label", theme === "light" ? "切换到深色模式" : "切换到浅色模式");
    }
    syncGiscusTheme(theme);
    if (window.__irRenderMermaid) window.__irRenderMermaid(theme);
  }

  function initTheme() {
    setTheme(currentTheme(), false);
    $$("[data-theme-toggle]").forEach((button) => {
      button.addEventListener("click", () => {
        setTheme(currentTheme() === "dark" ? "light" : "dark");
      });
    });
    window.addEventListener("load", () => {
      syncGiscusTheme(currentTheme());
      window.setTimeout(() => syncGiscusTheme(currentTheme()), 1200);
    });
    window.setTimeout(() => syncGiscusTheme(currentTheme()), 1600);
  }

  function syncGiscusTheme(theme) {
    const frame = $("iframe.giscus-frame");
    if (!frame || !frame.contentWindow) return;
    frame.contentWindow.postMessage(
      { giscus: { setConfig: { theme: theme === "light" ? "light" : "dark_dimmed" } } },
      "https://giscus.app"
    );
  }

  /* ------------------------------------------------------------------------
     Header, mobile menu, back to top
     ------------------------------------------------------------------------ */

  function initHeader() {
    const header = $("#siteHeader");
    if (header) {
      const onScroll = () => {
        header.classList.toggle("is-scrolled", window.scrollY > 8);
      };
      onScroll();
      window.addEventListener("scroll", onScroll, { passive: true });
    }

    const toggle = $("[data-menu-toggle]");
    const nav = $("#mobileNav");
    if (!toggle || !nav) return;

    const close = () => {
      toggle.setAttribute("aria-expanded", "false");
      toggle.setAttribute("aria-label", "打开导航菜单");
      nav.classList.remove("is-open");
      nav.setAttribute("aria-hidden", "true");
      document.body.classList.remove("no-scroll");
    };

    const open = () => {
      toggle.setAttribute("aria-expanded", "true");
      toggle.setAttribute("aria-label", "关闭导航菜单");
      nav.classList.add("is-open");
      nav.setAttribute("aria-hidden", "false");
      document.body.classList.add("no-scroll");
    };

    toggle.addEventListener("click", () => {
      if (toggle.getAttribute("aria-expanded") === "true") close();
      else open();
    });

    $$("a", nav).forEach((link) => link.addEventListener("click", close));
    window.addEventListener("resize", () => {
      if (window.innerWidth > 1020) close();
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && toggle.getAttribute("aria-expanded") === "true") close();
    });
  }

  function initBackToTop() {
    const button = $("[data-back-to-top]");
    if (!button) return;
    const update = () => {
      button.classList.toggle("is-visible", window.scrollY > 600);
    };
    update();
    window.addEventListener("scroll", update, { passive: true });
    $$("[data-back-to-top]").forEach((item) => {
      item.addEventListener("click", () => {
        window.scrollTo({ top: 0, behavior: prefersReducedMotion ? "auto" : "smooth" });
      });
    });
  }

  /* ------------------------------------------------------------------------
     Search palette
     ------------------------------------------------------------------------ */

  function initSearch() {
    const overlay = $("#searchOverlay");
    if (!overlay) return;
    const input = $("#searchInput");
    const resultsBox = $("#searchResults");
    const hints = $("#searchHints");
    const empty = $("#searchEmpty");
    const api = overlay.getAttribute("data-search-url");
    const triggers = $$("[data-search-open]");
    let controller = null;
    let timer = null;
    let items = [];
    let index = -1;

    const isOpen = () => overlay.classList.contains("is-open");

    function open() {
      overlay.classList.add("is-open");
      overlay.setAttribute("aria-hidden", "false");
      document.body.classList.add("no-scroll");
      window.setTimeout(() => input && input.focus(), 40);
      if (input && input.value.trim()) runSearch(input.value.trim());
    }

    function close() {
      overlay.classList.remove("is-open");
      overlay.setAttribute("aria-hidden", "true");
      document.body.classList.remove("no-scroll");
      if (controller) controller.abort();
      index = -1;
    }

    function setSelected(next) {
      if (!items.length) return;
      index = (next + items.length) % items.length;
      items.forEach((item, itemIndex) => {
        item.classList.toggle("is-selected", itemIndex === index);
      });
      items[index].scrollIntoView({ block: "nearest" });
    }

    function showHints() {
      hints.hidden = false;
      resultsBox.hidden = true;
      empty.hidden = true;
    }

    function showEmpty() {
      hints.hidden = true;
      resultsBox.hidden = true;
      empty.hidden = false;
    }

    function renderResults(payload) {
      const rows = Array.isArray(payload.results) ? payload.results : [];
      items = [];
      index = -1;
      resultsBox.replaceChildren();
      if (!rows.length) {
        showEmpty();
        return;
      }
      hints.hidden = true;
      empty.hidden = true;
      resultsBox.hidden = false;

      rows.forEach((row) => {
        const link = document.createElement("a");
        link.className = "search-result-item";
        link.href = row.url;

        const kind = document.createElement("span");
        kind.className = "search-result-kind";
        kind.textContent = row.kind || "页面";

        const copy = document.createElement("span");
        copy.className = "search-result-copy";
        const title = document.createElement("strong");
        title.textContent = row.title || "";
        const meta = document.createElement("small");
        meta.textContent = [row.meta, row.excerpt].filter(Boolean).join(" · ");
        copy.append(title, meta);

        link.append(kind, copy);
        link.addEventListener("mouseenter", () => {
          index = items.indexOf(link);
          items.forEach((item, itemIndex) => item.classList.toggle("is-selected", itemIndex === index));
        });
        resultsBox.append(link);
        items.push(link);
      });
    }

    function runSearch(query) {
      if (!api) return;
      if (controller) controller.abort();
      controller = new AbortController();
      fetch(`${api}?q=${encodeURIComponent(query)}`, {
        signal: controller.signal,
        headers: { Accept: "application/json" },
      })
        .then((response) => {
          if (!response.ok) throw new Error("search failed");
          return response.json();
        })
        .then(renderResults)
        .catch((error) => {
          if (error.name !== "AbortError") showEmpty();
        });
    }

    if (input) {
      input.addEventListener("input", () => {
        const query = input.value.trim();
        window.clearTimeout(timer);
        if (!query) {
          showHints();
          if (controller) controller.abort();
          return;
        }
        timer = window.setTimeout(() => runSearch(query), 140);
      });

      input.addEventListener("keydown", (event) => {
        if (event.key === "ArrowDown") {
          event.preventDefault();
          setSelected(index + 1);
        } else if (event.key === "ArrowUp") {
          event.preventDefault();
          setSelected(index - 1);
        } else if (event.key === "Enter" && index >= 0 && items[index]) {
          event.preventDefault();
          window.location.href = items[index].href;
        }
      });
    }

    $$("[data-search-suggest]").forEach((button) => {
      button.addEventListener("click", () => {
        if (!input) return;
        input.value = button.getAttribute("data-search-suggest") || "";
        input.focus();
        runSearch(input.value);
      });
    });

    triggers.forEach((trigger) => {
      trigger.addEventListener("click", (event) => {
        event.preventDefault();
        open();
      });
    });

    $$("[data-search-close]").forEach((button) => {
      button.addEventListener("click", close);
    });

    document.addEventListener("keydown", (event) => {
      const modifier = event.metaKey || event.ctrlKey;
      if (modifier && event.key.toLowerCase() === "k") {
        event.preventDefault();
        if (isOpen()) close();
        else open();
      }
      if (event.key === "Escape" && isOpen()) {
        event.preventDefault();
        close();
      }
      if (event.key === "Tab" && isOpen()) {
        const focusables = $$(
          'button, [href], input, [tabindex]:not([tabindex="-1"])',
          overlay
        ).filter((element) => !element.hasAttribute("disabled") && element.offsetParent !== null);
        if (!focusables.length) return;
        const first = focusables[0];
        const last = focusables[focusables.length - 1];
        if (event.shiftKey && document.activeElement === first) {
          event.preventDefault();
          last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault();
          first.focus();
        }
      }
      if (
        event.key === "/" &&
        !isOpen() &&
        !modifier &&
        !["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement.tagName) &&
        !document.activeElement.isContentEditable
      ) {
        event.preventDefault();
        open();
      }
    });

    const params = new URLSearchParams(window.location.search);
    if (window.location.pathname.endsWith("/search/") && params.get("q")) {
      /* The full search page owns this state; don't open the palette. */
    }
  }

  /* ------------------------------------------------------------------------
     Reading progress
     ------------------------------------------------------------------------ */

  function initReadingProgress() {
    const bar = $("[data-reading-progress]");
    const article = $("[data-article-content]");
    if (!bar || !article) return;

    const update = () => {
      const rect = article.getBoundingClientRect();
      const start = window.scrollY + rect.top;
      const height = Math.max(article.offsetHeight, 1);
      const viewport = window.innerHeight;
      const progress = Math.min(1, Math.max(0, (window.scrollY + viewport * 0.35 - start) / height));
      bar.style.width = `${progress * 100}%`;
    };
    update();
    window.addEventListener("scroll", update, { passive: true });
    window.addEventListener("resize", update);
  }

  /* ------------------------------------------------------------------------
     Table of contents
     ------------------------------------------------------------------------ */

  function initToc() {
    const toc = $("[data-toc]");
    const article = $("[data-article-content]");
    if (!toc || !article) return;

    const toggle = $("[data-toc-toggle]", toc);
    if (toggle) {
      toggle.addEventListener("click", () => {
        const collapsed = toc.classList.toggle("is-collapsed");
        toggle.setAttribute("aria-expanded", collapsed ? "false" : "true");
        toggle.setAttribute("aria-label", collapsed ? "展开目录" : "折叠目录");
      });
    }

    const links = $$("[data-toc-link]", toc);
    const byId = new Map();
    links.forEach((link) => {
      const id = decodeURIComponent((link.getAttribute("href") || "").replace(/^#/, ""));
      if (id) byId.set(id, link);
    });

    const headings = $$("h2[id], h3[id]", article).filter((heading) => byId.has(heading.id));
    if (!headings.length) return;

    let ticking = false;
    const update = () => {
      ticking = false;
      const headerOffset = 120;
      let active = headings[0];
      for (const heading of headings) {
        if (heading.getBoundingClientRect().top <= headerOffset) active = heading;
      }
      links.forEach((link) => link.parentElement.classList.remove("is-active"));
      const link = byId.get(active.id);
      if (link) link.parentElement.classList.add("is-active");
    };
    update();
    window.addEventListener(
      "scroll",
      () => {
        if (!ticking) {
          ticking = true;
          window.requestAnimationFrame(update);
        }
      },
      { passive: true }
    );
  }

  /* ------------------------------------------------------------------------
     Code copy + copy page link
     ------------------------------------------------------------------------ */

  async function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      return;
    }
    const textarea = document.createElement("textarea");
    textarea.value = text;
    textarea.setAttribute("readonly", "");
    textarea.style.position = "fixed";
    textarea.style.opacity = "0";
    document.body.append(textarea);
    textarea.select();
    document.execCommand("copy");
    textarea.remove();
  }

  function initCodeCopy() {
    $$(".code-copy").forEach((button) => {
      button.addEventListener("click", async () => {
        const figure = button.closest(".code-block");
        const code = figure ? $("code", figure) : null;
        if (!code) return;
        const clone = code.cloneNode(true);
        $$(".linenos", clone).forEach((lineNumber) => lineNumber.remove());
        try {
          await copyText(clone.textContent.replace(/\n$/, ""));
          button.classList.add("is-copied");
          const label = $("span", button);
          if (label) label.textContent = "已复制";
          const use = $("use", button);
          if (use) use.setAttribute("href", "#icon-check");
          window.setTimeout(() => {
            button.classList.remove("is-copied");
            if (label) label.textContent = "复制";
            if (use) use.setAttribute("href", "#icon-copy");
          }, 1800);
        } catch (error) {
          /* Clipboard permissions are optional. */
        }
      });
    });
  }

  function initCopyLink() {
    $$("[data-copy-link]").forEach((button) => {
      const label = $("span", button);
      const original = label ? label.textContent : "";
      button.addEventListener("click", async () => {
        try {
          await copyText(window.location.href);
          button.classList.add("is-copied");
          if (label) label.textContent = "已复制";
          window.setTimeout(() => {
            button.classList.remove("is-copied");
            if (label) label.textContent = original;
          }, 1800);
        } catch (error) {
          /* ignore */
        }
      });
    });
  }

  /* ------------------------------------------------------------------------
     Math and Mermaid
     ------------------------------------------------------------------------ */

  function initMath() {
    if (typeof window.renderMathInElement !== "function") return;
    const target = $("[data-article-content]") || $(".prose");
    if (!target) return;
    try {
      window.renderMathInElement(target, {
        delimiters: [
          { left: "\\[", right: "\\]", display: true },
          { left: "\\(", right: "\\)", display: false },
        ],
        throwOnError: false,
        ignoredTags: ["script", "noscript", "style", "textarea", "pre", "code", "option"],
      });
    } catch (error) {
      /* leave TeX readable when the CDN is unavailable */
    }
  }

  let mermaidAttempts = 0;

  function initMermaid() {
    if (!window.mermaid) {
      if (mermaidAttempts < 30) {
        mermaidAttempts += 1;
        window.setTimeout(initMermaid, 120);
      }
      return;
    }
    window.__irRenderMermaid = renderMermaid;
    renderMermaid(currentTheme());
  }

  async function renderMermaid(theme) {
    const diagrams = $$(".mermaid");
    if (!diagrams.length || !window.mermaid) return;
    try {
      window.mermaid.initialize({
        startOnLoad: false,
        theme: theme === "light" ? "neutral" : "dark",
        themeVariables: {
          fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace",
          fontSize: "12px",
        },
        securityLevel: "loose",
        flowchart: { curve: "basis", htmlLabels: true },
        sequence: { useMaxWidth: true },
      });
      for (const [index, diagram] of diagrams.entries()) {
        const source = diagram.dataset.source || diagram.textContent;
        diagram.dataset.source = source;
        const id = `ir-mermaid-${index}-${Date.now()}`;
        try {
          const result = await window.mermaid.render(id, source.trim());
          diagram.innerHTML = result.svg;
        } catch (error) {
          diagram.classList.add("mermaid-error");
          diagram.textContent = source;
        }
      }
    } catch (error) {
      /* Mermaid is decorative; never break the article. */
    }
  }

  /* ------------------------------------------------------------------------
     Project filters
     ------------------------------------------------------------------------ */

  function initProjectFilters() {
    const buttons = $$("[data-project-filter]");
    const grid = $("[data-project-grid]");
    if (!buttons.length || !grid) return;
    const cards = $$(".project-card", grid);
    const empty = $("[data-project-empty]");

    buttons.forEach((button) => {
      button.addEventListener("click", () => {
        const filter = button.getAttribute("data-project-filter");
        buttons.forEach((item) => item.classList.toggle("is-active", item === button));
        let visible = 0;
        cards.forEach((card) => {
          const matches = filter === "all" || card.getAttribute("data-category") === filter;
          card.classList.toggle("is-filtered-out", !matches);
          if (matches) visible += 1;
        });
        if (empty) empty.hidden = visible !== 0;
      });
    });
  }

  function initPrint() {
    $$("[data-print]").forEach((button) => {
      button.addEventListener("click", () => window.print());
    });
  }

  /* ------------------------------------------------------------------------
     Boot
     ------------------------------------------------------------------------ */

  function init() {
    initTheme();
    initHeader();
    initBackToTop();
    initSearch();
    initReadingProgress();
    initToc();
    initCodeCopy();
    initCopyLink();
    initMath();
    initMermaid();
    initProjectFilters();
    initPrint();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
