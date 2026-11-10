from __future__ import annotations

from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html

from .models import (
    Book,
    Category,
    Friend,
    Note,
    Post,
    Project,
    Status,
    Tag,
    ToolLink,
    Visit,
)

admin.site.site_header = "IR 之下 · 内容管理"
admin.site.site_title = "IR 之下"
admin.site.index_title = "写作与站点管理"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "icon", "accent", "order", "post_count")
    list_editable = ("order",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_post_count=Count("posts"))

    @admin.display(description="文章数", ordering="_post_count")
    def post_count(self, obj):
        return obj._post_count


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "accent", "published_count")
    list_filter = ("accent",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_published=Count("posts"))

    @admin.display(description="文章数", ordering="_published")
    def published_count(self, obj):
        return obj._published


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "status_badge",
        "is_featured",
        "reading_minutes",
        "views",
        "published_at",
    )
    list_filter = ("status", "category", "tags", "is_featured", "cover_style")
    search_fields = ("title", "summary", "content", "tags__name")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("tags",)
    date_hierarchy = "published_at"
    readonly_fields = ("reading_minutes", "views", "created_at", "updated_at", "word_count")
    list_per_page = 30
    fieldsets = (
        (
            "正文",
            {
                "fields": (
                    "title",
                    "slug",
                    "summary",
                    "content",
                    "category",
                    "tags",
                    "status",
                    "is_featured",
                    "cover_style",
                )
            },
        ),
        (
            "发布与统计",
            {
                "fields": (
                    "published_at",
                    "reading_minutes",
                    "word_count",
                    "views",
                    "created_at",
                    "updated_at",
                )
            },
        ),
        ("文末备注", {"fields": ("update_log", "errata"), "classes": ("collapse",)}),
    )

    @admin.display(description="状态", ordering="status")
    def status_badge(self, obj):
        color = "#1d9a72" if obj.status == Post.STATUS_PUBLISHED else "#8a8f98"
        return format_html(
            '<span style="color:{};font-weight:600">{}</span>',
            color,
            obj.get_status_display(),
        )

    @admin.display(description="字数")
    def word_count(self, obj):
        return len(obj.content or "")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "status", "progress", "is_featured", "sort_order", "updated_at")
    list_filter = ("category", "status", "is_featured")
    search_fields = ("title", "subtitle", "summary", "tech_stack")
    prepopulated_fields = {"slug": ("title",)}
    list_editable = ("is_featured", "sort_order")
    fieldsets = (
        (
            "项目信息",
            {
                "fields": (
                    "title",
                    "slug",
                    "subtitle",
                    "summary",
                    "description",
                    "category",
                    "status",
                    "progress",
                    "tech_stack",
                    "repo_url",
                    "demo_url",
                    "cover_style",
                )
            },
        ),
        ("展示", {"fields": ("is_featured", "sort_order", "launched_at", "updated_at")}),
    )
    readonly_fields = ("updated_at",)


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ("title", "note_type", "is_pinned", "updated_at", "tag_list")
    list_filter = ("note_type", "is_pinned", "tags")
    search_fields = ("title", "summary", "body", "aliases")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("tags",)
    fieldsets = (
        (
            "卡片",
            {
                "fields": (
                    "title",
                    "slug",
                    "summary",
                    "body",
                    "note_type",
                    "tags",
                    "aliases",
                    "is_pinned",
                )
            },
        ),
        ("时间", {"fields": ("created_at", "updated_at")}),
    )
    readonly_fields = ("created_at", "updated_at")

    @admin.display(description="标签")
    def tag_list(self, obj):
        return " / ".join(tag.name for tag in obj.tags.all())


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ("text", "mood", "is_visible", "created_at")
    list_filter = ("mood", "is_visible")
    list_editable = ("is_visible",)


@admin.register(Friend)
class FriendAdmin(admin.ModelAdmin):
    list_display = ("name", "url", "accent", "is_visible", "order")
    list_filter = ("accent", "is_visible")
    list_editable = ("is_visible", "order")


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "category", "status", "rating", "order")
    list_filter = ("category", "status", "rating")
    search_fields = ("title", "author", "review")
    list_editable = ("status", "rating", "order")


@admin.register(ToolLink)
class ToolLinkAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "url", "order")
    list_filter = ("category",)
    search_fields = ("name", "description", "url")
    list_editable = ("order",)


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ("day", "short_hash", "first_path", "created_at")
    list_filter = ("day",)
    search_fields = ("visitor_hash", "first_path")
    readonly_fields = ("day", "visitor_hash", "first_path", "created_at")

    @admin.display(description="访客")
    def short_hash(self, obj):
        return obj.visitor_hash[:10]

    def has_add_permission(self, request):
        return False
