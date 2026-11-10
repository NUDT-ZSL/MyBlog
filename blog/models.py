from __future__ import annotations

import re
import uuid
from datetime import date

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


def unique_slug(instance, value: str, slug_field: str = "slug") -> str:
    base = slugify(value, allow_unicode=True)[:80] or uuid.uuid4().hex[:8]
    candidate = base
    model = instance.__class__
    number = 2
    while model.objects.exclude(pk=instance.pk).filter(**{slug_field: candidate}).exists():
        candidate = f"{base}-{number}"
        number += 1
    return candidate


def estimate_reading_minutes(text: str) -> int:
    plain = re.sub(r"```.*?```", "", text, flags=re.S)
    plain = re.sub(r"[#>*_`~\-\[\]()!|]", "", plain)
    chinese = len(re.findall(r"[\u4e00-\u9fff]", plain))
    words = len(re.findall(r"[A-Za-z0-9_]+", plain))
    minutes = chinese / 320 + words / 220
    return max(1, round(minutes))


class Category(models.Model):
    ACCENTS = [
        ("jade", "玉青"),
        ("blue", "钴蓝"),
        ("amber", "琥珀"),
        ("rose", "陶红"),
        ("violet", "雾紫"),
    ]
    name = models.CharField("名称", max_length=40)
    slug = models.SlugField("Slug", max_length=60, unique=True, allow_unicode=True)
    description = models.CharField("描述", max_length=160, blank=True)
    icon = models.CharField("图标", max_length=8, default="◆")
    accent = models.CharField("强调色", max_length=12, choices=ACCENTS, default="jade")
    order = models.PositiveSmallIntegerField("排序", default=0)

    class Meta:
        verbose_name = "文章分类"
        verbose_name_plural = "文章分类"
        ordering = ["order", "id"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("blog:category_detail", args=[self.slug])

    @property
    def published_count(self):
        return self.posts.filter(
            status=Post.STATUS_PUBLISHED, published_at__lte=timezone.now()
        ).count()


class Tag(models.Model):
    name = models.CharField("名称", max_length=40)
    slug = models.SlugField("Slug", max_length=60, unique=True, allow_unicode=True)
    accent = models.CharField("强调色", max_length=12, choices=Category.ACCENTS, default="jade")

    class Meta:
        verbose_name = "标签"
        verbose_name_plural = "标签"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("blog:tag_detail", args=[self.slug])

    @property
    def published_count(self):
        return self.posts.filter(
            status=Post.STATUS_PUBLISHED, published_at__lte=timezone.now()
        ).count()


class Post(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_PUBLISHED = "published"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "草稿"),
        (STATUS_PUBLISHED, "已发布"),
    ]
    COVER_STYLES = [
        ("terminal", "终端"),
        ("blueprint", "蓝图"),
        ("graph", "图网络"),
        ("wave", "波形"),
        ("paper", "纸页"),
        ("jade", "玉色"),
    ]

    title = models.CharField("标题", max_length=160)
    slug = models.SlugField("Slug", max_length=180, unique=True, allow_unicode=True)
    summary = models.TextField("摘要", max_length=320)
    content = models.TextField("正文（Markdown）")
    category = models.ForeignKey(
        Category, verbose_name="分类", on_delete=models.PROTECT, related_name="posts"
    )
    tags = models.ManyToManyField(Tag, verbose_name="标签", blank=True, related_name="posts")
    status = models.CharField("状态", max_length=12, choices=STATUS_CHOICES, default=STATUS_PUBLISHED)
    is_featured = models.BooleanField("首页推荐", default=False)
    cover_style = models.CharField("封面样式", max_length=16, choices=COVER_STYLES, default="terminal")
    published_at = models.DateTimeField("发布时间", default=timezone.now)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)
    reading_minutes = models.PositiveSmallIntegerField("阅读时长（分钟）", default=1)
    views = models.PositiveIntegerField("阅读量", default=0)
    update_log = models.TextField("更新日志", blank=True)
    errata = models.TextField("勘误与讨论", blank=True)

    class Meta:
        verbose_name = "文章"
        verbose_name_plural = "文章"
        ordering = ["-published_at", "-id"]
        indexes = [models.Index(fields=["status", "-published_at"])]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.title)
        self.reading_minutes = estimate_reading_minutes(self.content)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:post_detail", args=[self.slug])

    @property
    def is_published(self):
        return self.status == self.STATUS_PUBLISHED and self.published_at <= timezone.now()

    @property
    def is_fresh(self):
        return (timezone.now() - self.published_at).days <= 10

    @property
    def accent(self):
        return self.category.accent if self.category_id else "jade"

    @property
    def tag_list(self):
        return list(self.tags.all())


class Project(models.Model):
    CATEGORY_RESEARCH = "research"
    CATEGORY_ENGINEERING = "engineering"
    CATEGORY_DEMO = "demo"
    CATEGORY_CHOICES = [
        (CATEGORY_RESEARCH, "科研"),
        (CATEGORY_ENGINEERING, "工程"),
        (CATEGORY_DEMO, "学习 Demo"),
    ]
    STATUS_LIVE = "live"
    STATUS_WIP = "wip"
    STATUS_ARCHIVED = "archived"
    STATUS_CHOICES = [
        (STATUS_LIVE, "持续维护"),
        (STATUS_WIP, "开发中"),
        (STATUS_ARCHIVED, "已归档"),
    ]

    title = models.CharField("名称", max_length=120)
    slug = models.SlugField("Slug", max_length=140, unique=True, allow_unicode=True)
    subtitle = models.CharField("一句话简介", max_length=240)
    summary = models.TextField("卡片简介", max_length=500)
    description = models.TextField("详情（Markdown）", blank=True)
    category = models.CharField("类别", max_length=16, choices=CATEGORY_CHOICES, default=CATEGORY_RESEARCH)
    status = models.CharField("状态", max_length=12, choices=STATUS_CHOICES, default=STATUS_LIVE)
    progress = models.PositiveSmallIntegerField("完成度", default=100)
    tech_stack = models.CharField("技术栈（逗号分隔）", max_length=240)
    repo_url = models.URLField("仓库链接", blank=True)
    demo_url = models.URLField("演示链接", blank=True)
    cover_style = models.CharField(
        "封面样式",
        max_length=20,
        choices=[
            ("cfg", "控制流图"),
            ("lattice", "格与数据流"),
            ("wave", "波形"),
            ("agent", "Agent 网络"),
            ("jade", "玉"),
            ("layers", "模型层"),
            ("algo", "算法图"),
            ("terminal", "终端"),
        ],
        default="cfg",
    )
    is_featured = models.BooleanField("首页精选", default=False)
    sort_order = models.PositiveSmallIntegerField("排序", default=0)
    launched_at = models.DateField("开始日期", default=date.today)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "项目"
        verbose_name_plural = "项目"
        ordering = ["sort_order", "-updated_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("blog:project_detail", args=[self.slug])

    @property
    def stack(self):
        return [part.strip() for part in self.tech_stack.split(",") if part.strip()]

    @property
    def is_wip(self):
        return self.status == self.STATUS_WIP


class Note(models.Model):
    TYPE_CONCEPT = "concept"
    TYPE_CHEATSHEET = "cheatsheet"
    TYPE_LOG = "log"
    TYPE_CHOICES = [
        (TYPE_CONCEPT, "概念卡片"),
        (TYPE_CHEATSHEET, "速查手册"),
        (TYPE_LOG, "碎片记录"),
    ]

    title = models.CharField("标题", max_length=120)
    slug = models.SlugField("Slug", max_length=140, unique=True, allow_unicode=True)
    summary = models.CharField("摘要", max_length=260)
    body = models.TextField("正文（Markdown，支持 [[双链]]）")
    note_type = models.CharField("类型", max_length=16, choices=TYPE_CHOICES, default=TYPE_CONCEPT)
    tags = models.ManyToManyField(Tag, verbose_name="标签", blank=True, related_name="notes")
    aliases = models.CharField("别名（逗号分隔）", max_length=200, blank=True)
    is_pinned = models.BooleanField("置顶", default=False)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "知识卡片"
        verbose_name_plural = "知识卡片"
        ordering = ["-is_pinned", "-updated_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("blog:note_detail", args=[self.slug])

    @property
    def alias_list(self):
        return [part.strip() for part in self.aliases.split(",") if part.strip()]

    @property
    def type_label(self):
        return dict(self.TYPE_CHOICES).get(self.note_type, "笔记")


class Status(models.Model):
    MOODS = [
        ("work", "调试中"),
        ("read", "阅读中"),
        ("build", "构建中"),
        ("life", "生活"),
    ]
    text = models.CharField("内容", max_length=240)
    mood = models.CharField("状态", max_length=12, choices=MOODS, default="work")
    is_visible = models.BooleanField("显示", default=True)
    created_at = models.DateTimeField("时间", default=timezone.now)

    class Meta:
        verbose_name = "碎碎念"
        verbose_name_plural = "碎碎念"
        ordering = ["-created_at"]

    def __str__(self):
        return self.text[:48]


class Friend(models.Model):
    name = models.CharField("名称", max_length=60)
    url = models.URLField("链接")
    description = models.CharField("简介", max_length=180)
    avatar_text = models.CharField("头像文字", max_length=4, default="友")
    accent = models.CharField("颜色", max_length=12, choices=Category.ACCENTS, default="jade")
    is_visible = models.BooleanField("显示", default=True)
    order = models.PositiveSmallIntegerField("排序", default=0)

    class Meta:
        verbose_name = "友链"
        verbose_name_plural = "友链"
        ordering = ["order", "id"]

    def __str__(self):
        return self.name


class Book(models.Model):
    STATUS_CHOICES = [
        ("reading", "在读"),
        ("finished", "读完"),
        ("queued", "待读"),
        ("reference", "常翻"),
    ]
    title = models.CharField("书名", max_length=120)
    author = models.CharField("作者", max_length=120)
    category = models.CharField("分类", max_length=40, default="专业")
    status = models.CharField("状态", max_length=12, choices=STATUS_CHOICES, default="queued")
    rating = models.PositiveSmallIntegerField("评分（1-5）", default=4)
    review = models.TextField("短评", max_length=500, blank=True)
    accent = models.CharField("书脊颜色", max_length=12, choices=Category.ACCENTS, default="jade")
    order = models.PositiveSmallIntegerField("排序", default=0)

    class Meta:
        verbose_name = "书单"
        verbose_name_plural = "书单"
        ordering = ["order", "-rating", "id"]

    def __str__(self):
        return self.title


class ToolLink(models.Model):
    name = models.CharField("名称", max_length=80)
    url = models.URLField("链接")
    description = models.CharField("简介", max_length=200)
    category = models.CharField("分类", max_length=40, default="常用")
    icon = models.CharField("图标字母", max_length=4, default="↗")
    order = models.PositiveSmallIntegerField("排序", default=0)

    class Meta:
        verbose_name = "工具链接"
        verbose_name_plural = "工具链接"
        ordering = ["category", "order", "id"]

    def __str__(self):
        return self.name


class Visit(models.Model):
    day = models.DateField("日期", default=date.today, db_index=True)
    visitor_hash = models.CharField("访客哈希", max_length=64)
    first_path = models.CharField("首次路径", max_length=255, blank=True)
    created_at = models.DateTimeField("首次访问", auto_now_add=True)

    class Meta:
        verbose_name = "访问记录"
        verbose_name_plural = "访问记录"
        constraints = [
            models.UniqueConstraint(fields=["day", "visitor_hash"], name="unique_daily_visitor")
        ]

    def __str__(self):
        return f"{self.day} · {self.visitor_hash[:8]}"
