"""Custom template tags for the content app."""

from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def meta_title(title: str, site_name: str) -> str:
    if not title:
        return site_name
    return f"{title} | {site_name}"


@register.filter
def reading_time(minutes: int) -> str:
    try:
        m = int(minutes)
    except Exception:
        m = 1
    return f"{m} min read"


@register.simple_tag
def og_meta(title: str, description: str, image_url: str | None = None) -> str:
    parts: list[str] = [
        f'<meta property="og:title" content="{title}">',
        f'<meta property="og:description" content="{description}">',
    ]
    if image_url:
        parts.append(f'<meta property="og:image" content="{image_url}">')
    return mark_safe("\n".join(parts))


@register.inclusion_tag("components/pagination.html", takes_context=True)
def render_pagination(context, page_obj):
    request = context["request"]
    return {"page_obj": page_obj, "request": request} 