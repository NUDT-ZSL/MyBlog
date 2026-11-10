from __future__ import annotations

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    query = context["request"].GET.copy()
    for key, value in kwargs.items():
        if value is None:
            query.pop(key, None)
        else:
            query[key] = value
    encoded = query.urlencode()
    return f"?{encoded}" if encoded else "."


@register.filter
def split_csv(value: str) -> list[str]:
    return [part.strip() for part in (value or "").split(",") if part.strip()]


@register.filter
def get_item(mapping, key):
    if hasattr(mapping, "get"):
        return mapping.get(key)
    return None


@register.filter
def stars(value: int) -> str:
    value = max(0, min(5, int(value or 0)))
    return "★" * value + "☆" * (5 - value)


@register.filter
def zh_date(value, fmt="Y.m.d"):
    if not value:
        return ""
    try:
        return value.strftime(fmt)
    except AttributeError:
        return value


@register.filter
def reading_label(minutes):
    minutes = max(1, int(minutes or 1))
    return f"{minutes} 分钟"


@register.filter
def strip_leading_slash(value: str) -> str:
    return (value or "").lstrip("/")


@register.simple_tag
def nav_active(current_url_name: str, *names) -> str:
    if current_url_name in names:
        return "is-active"
    return ""


@register.filter
def initials(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return "·"
    return value[0].upper()


@register.filter
def safe_join(values, separator=" · "):
    return separator.join(str(value) for value in values)


@register.simple_tag
def external_link_attrs(url: str) -> str:
    if url and url.startswith(("http://", "https://")):
        return mark_safe('target="_blank" rel="noopener noreferrer"')
    return ""
