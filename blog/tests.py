from __future__ import annotations

from datetime import timedelta

from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .markdown_renderer import render_markdown
from .models import Category, Note, Post, Tag, Visit


class BlogTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(
            name="科研笔记", slug="research", description="研究记录", icon="◈", accent="jade"
        )
        cls.tag = Tag.objects.create(name="LLVM", slug="llvm", accent="jade")
        cls.post = Post.objects.create(
            title="测试文章",
            slug="test-post",
            summary="一篇用于测试的文章。",
            content="""## 第一节

行内公式 $x^2$ 与代码：

```python
print("hello")
```

相关卡片：[[SSA]]。
""",
            category=cls.category,
            published_at=timezone.now() - timedelta(days=1),
        )
        cls.post.tags.add(cls.tag)
        cls.note = Note.objects.create(
            title="SSA",
            slug="ssa",
            summary="静态单赋值。",
            note_type=Note.TYPE_CONCEPT,
            body="SSA 是 [[支配边界]] 的基础。",
        )
        cls.note.tags.add(cls.tag)
        cls.other_note = Note.objects.create(
            title="支配边界",
            slug="dominance-frontier",
            summary="φ 的插入位置。",
            note_type=Note.TYPE_CONCEPT,
            body="支配边界与 [[SSA]] 密切相关。",
        )

    def test_home_and_list_pages(self):
        for url in [
            reverse("blog:home"),
            reverse("blog:post_list"),
            reverse("blog:project_list"),
            reverse("blog:note_list"),
            reverse("blog:archive"),
            reverse("blog:about"),
            reverse("blog:friends"),
            reverse("blog:books"),
            reverse("blog:tools"),
            reverse("blog:resume"),
        ]:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_post_detail_renders_markdown(self):
        response = self.client.get(self.post.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "toc-item")
        self.assertContains(response, "code-block")
        self.assertContains(response, "math-inline")
        self.assertContains(response, "/notes/ssa/")
        self.assertContains(response, "测试文章")

    def test_note_backlinks(self):
        response = self.client.get(self.note.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "反向链接")
        self.assertContains(response, self.other_note.get_absolute_url())

    def test_search_page_and_api(self):
        page = self.client.get(reverse("blog:search"), {"q": "SSA"})
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, "测试文章")
        api = self.client.get(reverse("blog:search_api"), {"q": "SSA"})
        self.assertEqual(api.status_code, 200)
        payload = api.json()
        self.assertGreaterEqual(payload["count"], 1)
        self.assertTrue(any("测试文章" == row["title"] for row in payload["results"]))

    def test_rss_and_sitemap(self):
        feed = self.client.get(reverse("blog:rss_feed"))
        self.assertEqual(feed.status_code, 200)
        self.assertIn("application/rss+xml", feed["Content-Type"])
        sitemap = self.client.get(reverse("sitemap"))
        self.assertEqual(sitemap.status_code, 200)
        self.assertIn("application/xml", sitemap["Content-Type"])

    def test_future_posts_are_hidden(self):
        Post.objects.create(
            title="未来文章",
            slug="future-post",
            summary="还没有发布。",
            content="未来。",
            category=self.category,
            published_at=timezone.now() + timedelta(days=10),
        )
        response = self.client.get(reverse("blog:post_list"))
        self.assertNotContains(response, "未来文章")

    def test_chinese_slug_is_reachable(self):
        post = Post.objects.create(
            title="中文标题",
            summary="自动生成中文 slug。",
            content="正文。",
            category=self.category,
            published_at=timezone.now() - timedelta(days=2),
        )
        self.assertIn("中文标题", post.slug)
        response = self.client.get(post.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_visit_counter_is_unique_per_day(self):
        client = Client(HTTP_USER_AGENT="test-browser")
        client.get(reverse("blog:home"))
        client.get(reverse("blog:post_list"))
        self.assertEqual(Visit.objects.count(), 1)

    def test_markdown_renderer_features(self):
        rendered = render_markdown(
            "## 标题\n\n```mermaid\nflowchart LR\nA-->B\n```\n\n$$x=1$$",
            {"ssa": "/notes/ssa/"},
        )
        self.assertIn("diagram-block", rendered.html)
        self.assertIn("math-display", rendered.html)
        self.assertEqual(rendered.toc[0].name, "标题")
        self.assertEqual(rendered.unresolved_links, 0)

    def test_custom_404(self):
        response = self.client.get("/this-page-does-not-exist/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "404", status_code=404)
