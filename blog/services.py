from __future__ import annotations

from datetime import date

from django.db.models import Count, Q
from django.utils import timezone

from .models import Category, Note, Post, Tag, Visit
from .markdown_renderer import normalize_link_key


def published_posts():
    return (
        Post.objects.filter(
            status=Post.STATUS_PUBLISHED,
            published_at__lte=timezone.now(),
        )
        .select_related("category")
        .prefetch_related("tags")
    )


def sidebar_context() -> dict:
    category_rows = (
        Category.objects.annotate(
            post_count=Count(
                "posts", filter=Q(posts__status=Post.STATUS_PUBLISHED, posts__published_at__lte=timezone.now()), distinct=True
            )
        )
        .filter(post_count__gt=0)
        .order_by("order", "id")
    )
    tag_rows = (
        Tag.objects.annotate(
            post_count=Count(
                "posts", filter=Q(posts__status=Post.STATUS_PUBLISHED, posts__published_at__lte=timezone.now()), distinct=True
            )
        )
        .filter(post_count__gt=0)
        .order_by("-post_count", "name")[:18]
    )
    popular = published_posts().order_by("-views", "-published_at")[:5]
    today = date.today()
    today_visitors = Visit.objects.filter(day=today).count()
    total_visitors = Visit.objects.values("visitor_hash").distinct().count()
    total_posts = published_posts().count()
    total_notes = Note.objects.count()
    return {
        "sidebar_categories": category_rows,
        "sidebar_tags": tag_rows,
        "popular_posts": popular,
        "today_visitors": today_visitors,
        "total_visitors": total_visitors,
        "total_posts": total_posts,
        "total_notes": total_notes,
        "sidebar_today": today,
    }


def note_link_index() -> dict[str, str]:
    mapping: dict[str, str] = {}
    for note in Note.objects.all():
        url = note.get_absolute_url()
        for key in [note.title, note.slug, *note.alias_list]:
            mapping[normalize_link_key(key)] = url
    return mapping


def note_backlinks(note: Note) -> list[Note]:
    from .markdown_renderer import extract_wiki_targets

    current_keys = {normalize_link_key(note.title), normalize_link_key(note.slug)}
    current_keys.update(normalize_link_key(alias) for alias in note.alias_list)
    linked_by = []
    for candidate in Note.objects.exclude(pk=note.pk).prefetch_related("tags"):
        if extract_wiki_targets(candidate.body) & current_keys:
            linked_by.append(candidate)
    return linked_by


def note_outgoing_links(note: Note) -> list[Note]:
    from .markdown_renderer import extract_wiki_targets

    targets = extract_wiki_targets(note.body)
    if not targets:
        return []
    outgoing = []
    for candidate in Note.objects.exclude(pk=note.pk):
        keys = {normalize_link_key(candidate.title), normalize_link_key(candidate.slug)}
        keys.update(normalize_link_key(alias) for alias in candidate.alias_list)
        if targets & keys:
            outgoing.append(candidate)
    return outgoing


def archive_groups() -> list[dict]:
    posts = published_posts().order_by("-published_at")
    years: list[dict] = []
    year_map: dict[int, dict] = {}
    month_map: dict[tuple[int, int], dict] = {}
    for post in posts:
        year = post.published_at.year
        month = post.published_at.month
        if year not in year_map:
            entry = {"year": year, "count": 0, "months": []}
            year_map[year] = entry
            years.append(entry)
        year_map[year]["count"] += 1
        key = (year, month)
        if key not in month_map:
            month_entry = {"month": month, "label": f"{month:02d} 月", "posts": []}
            month_map[key] = month_entry
            year_map[year]["months"].append(month_entry)
        month_map[key]["posts"].append(post)
    return years
