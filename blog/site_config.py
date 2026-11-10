"""Single source of truth for the personal bits of the site.

Everything here is intentionally plain Python: edit this file, restart the
server, and the header, hero, about page and footer update together.
The persona is demo content; replace the links and copy with your own.
"""
from __future__ import annotations

SITE = {
    "name": "IR 之下",
    "name_en": "UNDER THE IR",
    "owner": "林序",
    "handle": "linxu",
    "role": "博士一年级 · 高可信软件",
    "lab": "高可信软件课题组",
    "slogan": "代码、逻辑与细碎日常",
    "slogan_en": "Code, logic, and the little things in between.",
    "description": "博一在读，研究高可信软件与程序分析。白天和 LLVM IR 搏斗，偶尔雕玉、打游戏、记录一些还没想明白的问题。",
    "hero_kicker": "PhD Year 1 / Trusted Software",
    "hero_title_a": "在 IR 之间，",
    "hero_title_b": "寻找可被证明的秩序。",
    "hero_text": "我关心程序为什么正确，也关心它如何变得更快、更可解释。这里存放论文笔记、工程踩坑，以及代码之外的一点生活。",
    "location": "长沙",
    "status": "正在做 LLVM 数据流分析，也开放编译器 / 程序分析方向的交流。",
    "email": "linxu@example.edu",
    "email_note": "学术邮箱优先",
    "github": "https://github.com/linxu",
    "gitee": "https://gitee.com/linxu",
    "scholar": "https://scholar.google.com/",
    "site_repo": "https://github.com/linxu/ir-notes",
    "avatar": "img/avatar.svg",
    "started_year": 2024,
    "keywords": [
        "高可信软件",
        "LLVM Pass",
        "静态分析",
        "Verilog",
        "大模型微调",
        "全栈开发",
    ],
}

NAV_ITEMS = [
    {"label": "首页", "url_name": "home", "match": "home"},
    {"label": "文章", "url_name": "post_list", "match": "post"},
    {"label": "项目", "url_name": "project_list", "match": "project"},
    {"label": "笔记", "url_name": "note_list", "match": "note"},
    {"label": "归档", "url_name": "archive", "match": "archive"},
    {"label": "关于", "url_name": "about", "match": "about"},
    {"label": "友链", "url_name": "friends", "match": "friends"},
]

SOCIALS = [
    {"label": "GitHub", "url": SITE["github"], "icon": "github"},
    {"label": "Email", "url": "mailto:" + SITE["email"], "icon": "mail"},
    {"label": "Gitee", "url": SITE["gitee"], "icon": "git-branch"},
]

QUICK_LINKS = [
    {
        "label": "论文笔记",
        "caption": "Paper notes",
        "url_name": "tag_detail",
        "url_arg": "paper-reading",
        "icon": "file-text",
    },
    {
        "label": "开源项目",
        "caption": "Open source",
        "url_name": "project_list",
        "url_arg": None,
        "icon": "code",
    },
    {
        "label": "碎碎念",
        "caption": "Small talks",
        "url_name": "tag_detail",
        "url_arg": "life",
        "icon": "pen-line",
    },
]

STACK_GROUPS = [
    {
        "title": "编译与程序分析",
        "icon": "cpu",
        "items": ["LLVM / Clang", "C++17", "Data-flow Analysis", "SSA", "抽象解释"],
    },
    {
        "title": "硬件与验证",
        "icon": "circuit",
        "items": ["Verilog", "SystemVerilog", "Verilator", "Vivado", "UVM（学习中）"],
    },
    {
        "title": "后端与工程",
        "icon": "server",
        "items": ["Python", "Django", "Java / Spring", "Docker", "Nginx", "Linux"],
    },
    {
        "title": "AI 与工具",
        "icon": "sparkles",
        "items": ["PyTorch", "LoRA / PEFT", "vLLM", "Agent", "Git"],
    },
]

CURRENT_PLAN = [
    {
        "period": "NOW",
        "title": "把数据流分析做扎实",
        "text": "从经典到达不动点，到 LLVM New PM 里可复用、可测试的分析 Pass。",
        "done": False,
    },
    {
        "period": "2026 Q4",
        "title": "完成第一篇系统性论文笔记",
        "text": "围绕静态分析中的抽象解释与不变式生成，整理成可引用的中文长文。",
        "done": False,
    },
    {
        "period": "2026 Q3",
        "title": "Verilog 验证小闭环",
        "text": "用 Verilator 搭一套可复现的 UART 仿真与覆盖率流程。",
        "done": True,
    },
    {
        "period": "2025 Q4",
        "title": "这个站点上线",
        "text": "用 Django 搭一个自己愿意长期写下去的地方，而不是一次性作品集。",
        "done": True,
    },
]

RESEARCH_INTERESTS = [
    "高可信软件与程序验证",
    "静态分析 / 抽象解释",
    "LLVM 中间表示与优化 Pass",
    "AI for Code / Agent + 程序分析",
]

HOBBIES = [
    {"icon": "gamepad", "title": "游戏", "text": "偏爱有系统深度的策略与动作游戏，会研究机制，也会为帧数折腾。"},
    {"icon": "dumbbell", "title": "健身", "text": "把训练当编译优化：先测量，再改 IR，最后看真实收益。"},
    {"icon": "gem", "title": "玉器", "text": "家里有一间小小的玉器店「玉锦轩」，喜欢看料、看工、看光。"},
    {"icon": "wrench", "title": "折腾", "text": "软路由、Ventoy、旧笔记本再利用，以及一切本可以不必折腾的东西。"},
]

SITE_NOTES = {
    "stack": "Django 6 · SQLite · 手写 CSS · Pygments · KaTeX · Mermaid",
    "hosting": "可部署于任意支持 WSGI 的服务器，或使用 Gunicorn + Nginx。",
    "disclaimer": "学术内容均为个人学习记录，可能存在疏漏；欢迎指正，但请以原始论文与官方文档为准。",
    "copyright": "除特别注明外，本站文字采用 CC BY-NC-SA 4.0 许可，代码示例采用 MIT 许可。",
}

FOOTER_LINKS = [
    {"label": "书单", "url_name": "books"},
    {"label": "工具箱", "url_name": "tools"},
    {"label": "简历", "url_name": "resume"},
    {"label": "RSS", "url_name": "rss_feed", "external": True},
    {"label": "站点地图", "url_name": "sitemap", "external": True},
]
