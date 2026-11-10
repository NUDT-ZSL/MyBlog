"""Template context shared by every page."""
from __future__ import annotations

from datetime import date

from django.conf import settings
from django.urls import reverse

from .site_config import (
    CURRENT_PLAN,
    FOOTER_LINKS,
    HOBBIES,
    NAV_ITEMS,
    QUICK_LINKS,
    RESEARCH_INTERESTS,
    SITE,
    SITE_NOTES,
    SOCIALS,
    STACK_GROUPS,
)


def site_context(request):
    nav_items = []
    for item in NAV_ITEMS:
        try:
            url = reverse(f"blog:{item['url_name']}")
        except Exception:
            url = "/"
        nav_items.append({**item, "url": url})

    quick_links = []
    for item in QUICK_LINKS:
        if item["url_arg"]:
            url = reverse(f"blog:{item['url_name']}", args=[item["url_arg"]])
        else:
            url = reverse(f"blog:{item['url_name']}")
        quick_links.append({**item, "url": url})

    footer_links = []
    for item in FOOTER_LINKS:
        target = item["url_name"]
        try:
            if ":" in target:
                url = reverse(target)
            else:
                try:
                    url = reverse(f"blog:{target}")
                except Exception:
                    url = reverse(target)
            footer_links.append({**item, "url": url})
        except Exception:
            footer_links.append({**item, "url": "#"})

    resolver = getattr(request, "resolver_match", None)
    current_url_name = resolver.url_name if resolver else ""
    current_namespace = resolver.namespace if resolver else ""
    current_match = current_url_name.replace("_detail", "").replace("_list", "")

    return {
        "site": SITE,
        "nav_items": nav_items,
        "socials": SOCIALS,
        "quick_links": quick_links,
        "stack_groups": STACK_GROUPS,
        "current_plan": CURRENT_PLAN,
        "research_interests": RESEARCH_INTERESTS,
        "hobbies": HOBBIES,
        "site_notes": SITE_NOTES,
        "footer_links": footer_links,
        "site_url": settings.SITE_URL,
        "current_year": date.today().year,
        "current_url_name": current_url_name,
        "current_namespace": current_namespace,
        "current_match": current_match,
        "is_demo": settings.DEMO_MODE,
    }


def giscus_context(request):
    config = settings.GISCUS
    enabled = bool(config.get("repo") and config.get("repo_id"))
    return {"giscus": config, "giscus_enabled": enabled}
