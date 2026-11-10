from __future__ import annotations

from django.contrib.syndication.views import Feed
from django.urls import reverse
from django.utils import timezone
from django.utils.feedgenerator import Rss201rev2Feed

from .models import Post
from .site_config import SITE


class LatestPostsFeed(Feed):
    title = f"{SITE['name']} · {SITE['slogan']}"
    link = "/feed/"
    description = SITE["description"]
    feed_type = Rss201rev2Feed
    ttl = 60

    def items(self):
        return Post.objects.filter(
            status=Post.STATUS_PUBLISHED, published_at__lte=timezone.now()
        ).order_by("-published_at")[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.summary

    def item_link(self, item):
        return item.get_absolute_url()

    def item_pubdate(self, item):
        return item.published_at

    def item_updateddate(self, item):
        return item.updated_at

    def item_categories(self, item):
        return [item.category.name, *[tag.name for tag in item.tags.all()]]

    def item_author_name(self, item):
        return SITE["owner"]

    def feed_extra_kwargs(self, obj):
        return {"docs": "https://www.rssboard.org/rss-specification"}

    def item_extra_kwargs(self, item):
        return {"guid": f"{SITE['name']}:{item.slug}"}

    def link(self):
        return reverse("blog:post_list")
