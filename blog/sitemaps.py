from __future__ import annotations

from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone

from .models import Note, Post, Project


class BlogSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return list(
            Post.objects.filter(
                status=Post.STATUS_PUBLISHED, published_at__lte=timezone.now()
            ).order_by("-published_at")[:500]
        )

    def location(self, item):
        return item.get_absolute_url()

    def lastmod(self, item):
        return item.updated_at


class NoteSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return list(Note.objects.all()[:500])

    def location(self, item):
        return item.get_absolute_url()

    def lastmod(self, item):
        return item.updated_at


class ProjectSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return list(Project.objects.all()[:200])

    def location(self, item):
        return item.get_absolute_url()

    def lastmod(self, item):
        return item.updated_at


class PageSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return [
            "home",
            "post_list",
            "project_list",
            "note_list",
            "archive",
            "about",
            "friends",
            "books",
            "tools",
            "resume",
        ]

    def location(self, item):
        return reverse(f"blog:{item}")

    def lastmod(self, item):
        from django.utils import timezone

        return timezone.now()
