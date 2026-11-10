from __future__ import annotations

from collections import defaultdict
from django.conf import settings
from django.db.models import Count, Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET

from .markdown_renderer import normalize_link_key, render_markdown
from .models import Book, Category, Friend, Note, Post, Project, Status, Tag, ToolLink
from .services import (
    archive_groups,
    note_backlinks,
    note_link_index,
    note_outgoing_links,
    published_posts,
    sidebar_context,
)


def _base_context(**extra):
    context = {"page_title": None, "page_description": None}
    context.update(extra)
    return context


def _paginate(request, queryset, per_page=8):
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(request.GET.get("page"))


def home(request):
    recent_posts = list(published_posts().order_by("-published_at")[:6])
    featured_projects = list(
        Project.objects.filter(is_featured=True).order_by("sort_order", "-updated_at")[:3]
    )
    if len(featured_projects) < 3:
        featured_ids = [project.pk for project in featured_projects]
        featured_projects += list(
            Project.objects.exclude(pk__in=featured_ids).order_by("sort_order", "-updated_at")[
                : 3 - len(featured_projects)
            ]
        )
    statuses = list(Status.objects.filter(is_visible=True)[:4])
    latest_notes = list(Note.objects.prefetch_related("tags").order_by("-updated_at")[:3])
    latest_note = latest_notes[0] if latest_notes else None
    total_views = published_posts().aggregate(total=Sum("views"))["total"]
    context = _base_context(
        recent_posts=recent_posts,
        featured_projects=featured_projects,
        statuses=statuses,
        latest_note=latest_note,
        latest_notes=latest_notes,
        total_views=total_views or 0,
        page_title=None,
        page_description="高可信软件、LLVM 与静态分析的个人笔记，也记录工程实践和细碎日常。",
        body_class="page-home",
    )
    context.update(sidebar_context())
    return render(request, "blog/home.html", context)


def post_list(request):
    posts = published_posts().order_by("-published_at")
    query = request.GET.get("q", "").strip()
    if query:
        posts = posts.filter(
            Q(title__icontains=query)
            | Q(summary__icontains=query)
            | Q(content__icontains=query)
            | Q(tags__name__icontains=query)
        ).distinct()
    page = _paginate(request, posts)
    categories = Category.objects.annotate(
        post_count=Count("posts", filter=Q(posts__status=Post.STATUS_PUBLISHED, posts__published_at__lte=timezone.now()), distinct=True)
    ).filter(post_count__gt=0)
    context = _base_context(
        page_obj=page,
        posts=page.object_list,
        categories=categories,
        query=query,
        page_title="文章",
        page_description="科研笔记、工程实践、算法竞赛与兴趣随笔。",
        body_class="page-posts",
        section="posts",
    )
    context.update(sidebar_context())
    return render(request, "blog/post_list.html", context)


def post_detail(request, slug):
    post = get_object_or_404(
        published_posts().filter(status=Post.STATUS_PUBLISHED), slug=slug
    )
    viewed = request.session.get("viewed_posts", [])
    if post.pk not in viewed:
        Post.objects.filter(pk=post.pk).update(views=post.views + 1)
        post.views += 1
        viewed = (viewed + [post.pk])[-80:]
        request.session["viewed_posts"] = viewed

    note_links = note_link_index()
    rendered = render_markdown(post.content, note_links=note_links)
    tag_ids = list(post.tags.values_list("id", flat=True))
    related = (
        Post.objects.filter(status=Post.STATUS_PUBLISHED)
        .filter(Q(category=post.category) | Q(tags__id__in=tag_ids))
        .exclude(pk=post.pk)
        .select_related("category")
        .prefetch_related("tags")
        .distinct()
        .order_by("-published_at")[:3]
    )
    if len(related) < 3:
        existing = [item.pk for item in related]
        related = list(related) + list(
            Post.objects.filter(status=Post.STATUS_PUBLISHED)
            .exclude(pk__in=existing + [post.pk])
            .select_related("category")
            .prefetch_related("tags")
            .order_by("-published_at")[: 3 - len(related)]
        )
    previous_post = (
        Post.objects.filter(status=Post.STATUS_PUBLISHED, published_at__lt=post.published_at)
        .order_by("-published_at")
        .first()
    )
    next_post = (
        Post.objects.filter(status=Post.STATUS_PUBLISHED, published_at__gt=post.published_at)
        .order_by("published_at")
        .first()
    )
    context = _base_context(
        post=post,
        rendered=rendered,
        toc=rendered.toc,
        related_posts=related,
        previous_post=previous_post,
        next_post=next_post,
        page_title=post.title,
        page_description=post.summary,
        body_class="page-post",
        section="posts",
        canonical_path=post.get_absolute_url(),
        og_type="article",
    )
    return render(request, "blog/post_detail.html", context)


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    page = _paginate(
        request,
        published_posts().filter(category=category).order_by("-published_at"),
    )
    context = _base_context(
        category=category,
        page_obj=page,
        posts=page.object_list,
        page_title=category.name,
        page_description=category.description or f"{category.name}分类下的全部文章。",
        body_class="page-posts page-category",
        section="posts",
    )
    context.update(sidebar_context())
    return render(request, "blog/post_list.html", context)


def tag_detail(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    page = _paginate(
        request,
        published_posts().filter(tags=tag).order_by("-published_at"),
    )
    notes = Note.objects.filter(tags=tag)
    context = _base_context(
        tag=tag,
        page_obj=page,
        posts=page.object_list,
        tag_notes=notes,
        page_title=f"#{tag.name}",
        page_description=f"带有「{tag.name}」标签的文章与笔记。",
        body_class="page-posts page-tag",
        section="posts",
    )
    context.update(sidebar_context())
    return render(request, "blog/post_list.html", context)


@require_GET
def project_list(request):
    projects = list(Project.objects.all())
    counts = {
        "all": len(projects),
        "research": sum(1 for project in projects if project.category == Project.CATEGORY_RESEARCH),
        "engineering": sum(
            1 for project in projects if project.category == Project.CATEGORY_ENGINEERING
        ),
        "demo": sum(1 for project in projects if project.category == Project.CATEGORY_DEMO),
        "wip": sum(1 for project in projects if project.status == Project.STATUS_WIP),
    }
    featured = [project for project in projects if project.is_featured][:3]
    wip_projects = [project for project in projects if project.status == Project.STATUS_WIP]
    shipped_projects = [project for project in projects if project.status != Project.STATUS_WIP]
    context = _base_context(
        projects=projects,
        featured_projects=featured,
        wip_projects=wip_projects,
        shipped_projects=shipped_projects,
        project_counts=counts,
        page_title="项目",
        page_description="科研原型、工程实践与学习 Demo。",
        body_class="page-projects",
        section="projects",
    )
    return render(request, "blog/project_list.html", context)


def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)
    rendered = render_markdown(project.description, note_links=note_link_index()) if project.description else None
    related = Project.objects.exclude(pk=project.pk).order_by("?")[:2]
    context = _base_context(
        project=project,
        rendered=rendered,
        related_projects=related,
        page_title=project.title,
        page_description=project.subtitle,
        body_class="page-project-detail",
        section="projects",
    )
    return render(request, "blog/project_detail.html", context)


def note_list(request):
    notes = Note.objects.prefetch_related("tags")
    note_type = request.GET.get("type", "").strip()
    tag_slug = request.GET.get("tag", "").strip()
    query = request.GET.get("q", "").strip()
    if note_type in dict(Note.TYPE_CHOICES):
        notes = notes.filter(note_type=note_type)
    selected_tag = None
    if tag_slug:
        selected_tag = get_object_or_404(Tag, slug=tag_slug)
        notes = notes.filter(tags=selected_tag)
    if query:
        notes = notes.filter(
            Q(title__icontains=query) | Q(summary__icontains=query) | Q(body__icontains=query)
        )
    type_counts = {
        row["note_type"]: row["count"]
        for row in Note.objects.values("note_type").annotate(count=Count("id"))
    }
    note_tags = (
        Tag.objects.filter(notes__isnull=False)
        .annotate(note_count=Count("notes"))
        .order_by("-note_count", "name")[:14]
    )
    context = _base_context(
        notes=notes,
        note_type=note_type,
        selected_tag=selected_tag,
        query=query,
        type_counts=type_counts,
        note_tags=note_tags,
        total_notes=Note.objects.count(),
        page_title="知识库",
        page_description="SSA、支配边界、抽象解释、FIR 与工程速查卡；一个持续生长的第二大脑。",
        body_class="page-notes",
        section="notes",
    )
    return render(request, "blog/note_list.html", context)


def note_detail(request, slug):
    note = get_object_or_404(Note, slug=slug)
    note_links = note_link_index()
    rendered = render_markdown(note.body, note_links=note_links)
    backlinks = note_backlinks(note)
    outgoing = note_outgoing_links(note)
    related = (
        Note.objects.filter(tags__in=note.tags.all())
        .exclude(pk=note.pk)
        .distinct()
        .prefetch_related("tags")[:4]
    )
    context = _base_context(
        note=note,
        rendered=rendered,
        toc=rendered.toc,
        backlinks=backlinks,
        outgoing_links=outgoing,
        related_notes=related,
        page_title=note.title,
        page_description=note.summary,
        body_class="page-note-detail",
        section="notes",
    )
    return render(request, "blog/note_detail.html", context)


@require_GET
def archive(request):
    groups = archive_groups()
    categories = Category.objects.annotate(
        post_count=Count("posts", filter=Q(posts__status=Post.STATUS_PUBLISHED, posts__published_at__lte=timezone.now()), distinct=True)
    ).filter(post_count__gt=0)
    tags = (
        Tag.objects.annotate(
            post_count=Count(
                "posts", filter=Q(posts__status=Post.STATUS_PUBLISHED, posts__published_at__lte=timezone.now()), distinct=True
            )
        )
        .filter(post_count__gt=0)
        .order_by("-post_count", "name")
    )
    total_posts = sum(group["count"] for group in groups)
    context = _base_context(
        groups=groups,
        categories=categories,
        tags=tags,
        total_posts=total_posts,
        page_title="归档",
        page_description="按时间、分类与标签浏览全部文章。",
        body_class="page-archive",
        section="archive",
    )
    return render(request, "blog/archive.html", context)


@require_GET
def search(request):
    query = request.GET.get("q", "").strip()[:80]
    posts = []
    notes = []
    projects = []
    if query:
        posts = list(
            published_posts()
            .filter(
                Q(title__icontains=query)
                | Q(summary__icontains=query)
                | Q(content__icontains=query)
                | Q(tags__name__icontains=query)
            )
            .distinct()
            .order_by("-published_at")[:30]
        )
        notes = list(
            Note.objects.filter(
                Q(title__icontains=query)
                | Q(summary__icontains=query)
                | Q(body__icontains=query)
            )
            .distinct()
            .order_by("-updated_at")[:30]
        )
        projects = list(
            Project.objects.filter(
                Q(title__icontains=query)
                | Q(subtitle__icontains=query)
                | Q(summary__icontains=query)
                | Q(tech_stack__icontains=query)
            ).order_by("sort_order")[:20]
        )
    total = len(posts) + len(notes) + len(projects)
    context = _base_context(
        query=query,
        posts=posts,
        notes=notes,
        projects=projects,
        total=total,
        page_title="搜索" if not query else f"搜索：{query}",
        page_description="搜索文章、知识卡片与项目。",
        body_class="page-search",
        section="search",
    )
    return render(request, "blog/search.html", context)


@require_GET
def search_api(request):
    query = request.GET.get("q", "").strip()[:80]
    results = []
    if query:
        post_rows = (
            published_posts()
            .filter(
                Q(title__icontains=query)
                | Q(summary__icontains=query)
                | Q(content__icontains=query)
                | Q(tags__name__icontains=query)
            )
            .distinct()
            .order_by("-published_at")[:5]
        )
        for post in post_rows:
            results.append(
                {
                    "title": post.title,
                    "url": post.get_absolute_url(),
                    "kind": "文章",
                    "meta": post.category.name,
                    "excerpt": post.summary[:90],
                }
            )
        note_rows = (
            Note.objects.filter(
                Q(title__icontains=query)
                | Q(summary__icontains=query)
                | Q(body__icontains=query)
            )
            .distinct()
            .order_by("-updated_at")[:4]
        )
        for note in note_rows:
            results.append(
                {
                    "title": note.title,
                    "url": note.get_absolute_url(),
                    "kind": "笔记",
                    "meta": note.type_label,
                    "excerpt": note.summary[:90],
                }
            )
        project_rows = Project.objects.filter(
            Q(title__icontains=query)
            | Q(subtitle__icontains=query)
            | Q(tech_stack__icontains=query)
        ).order_by("sort_order")[:3]
        for project in project_rows:
            results.append(
                {
                    "title": project.title,
                    "url": project.get_absolute_url(),
                    "kind": "项目",
                    "meta": project.get_category_display(),
                    "excerpt": project.subtitle[:90],
                }
            )
    return JsonResponse({"query": query, "count": len(results), "results": results})


def about(request):
    counts = {
        "posts": published_posts().count(),
        "notes": Note.objects.count(),
        "projects": Project.objects.count(),
        "views": published_posts().aggregate(total=Sum("views"))["total"] or 0,
    }
    context = _base_context(
        counts=counts,
        statuses=Status.objects.filter(is_visible=True)[:3],
        page_title="关于",
        page_description="关于林序：高可信软件、LLVM、静态分析与代码之外的生活。",
        body_class="page-about",
        section="about",
    )
    return render(request, "blog/about.html", context)


def friends(request):
    context = _base_context(
        friends=Friend.objects.filter(is_visible=True),
        page_title="友链",
        page_description="同行、常读的博客，以及一些值得反复访问的角落。",
        body_class="page-friends",
        section="friends",
    )
    return render(request, "blog/friends.html", context)


def books(request):
    rows = list(Book.objects.all())
    grouped: dict[str, list[Book]] = defaultdict(list)
    for book in rows:
        grouped[book.category].append(book)
    status_counts = {
        "reading": sum(1 for book in rows if book.status == "reading"),
        "finished": sum(1 for book in rows if book.status == "finished"),
        "queued": sum(1 for book in rows if book.status == "queued"),
    }
    context = _base_context(
        grouped_books=dict(grouped),
        total_books=len(rows),
        status_counts=status_counts,
        page_title="书单",
        page_description="专业书、闲书，以及读完之后留下的一点笔记。",
        body_class="page-books",
        section="books",
    )
    return render(request, "blog/books.html", context)


def tools(request):
    rows = list(ToolLink.objects.all())
    grouped: dict[str, list[ToolLink]] = defaultdict(list)
    for tool in rows:
        grouped[tool.category].append(tool)
    context = _base_context(
        grouped_tools=dict(grouped),
        total_tools=len(rows),
        page_title="工具箱",
        page_description="编译器、程序分析、硬件验证与论文检索的常用入口。",
        body_class="page-tools",
        section="tools",
    )
    return render(request, "blog/tools.html", context)


def resume(request):
    counts = {
        "posts": published_posts().count(),
        "projects": Project.objects.count(),
    }
    context = _base_context(
        counts=counts,
        resume_projects=Project.objects.order_by("sort_order")[:4],
        page_title="简历",
        page_description="一份简洁的在线简历：研究方向、工程项目与技术栈。",
        body_class="page-resume",
        section="resume",
    )
    return render(request, "blog/resume.html", context)


def custom_404(request, exception):
    return render(
        request,
        "404.html",
        _base_context(
            page_title="页面走丢了",
            page_description="这个地址没有对应的页面。",
            body_class="page-404",
        ),
        status=404,
    )


@require_GET
def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        f"Sitemap: {settings.SITE_URL}{reverse('sitemap')}",
    ]
    from django.http import HttpResponse

    return HttpResponse("\n".join(lines), content_type="text/plain; charset=utf-8")
