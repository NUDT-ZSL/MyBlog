from __future__ import annotations

import hashlib
import logging

from django.conf import settings
from django.db import DatabaseError
from django.utils import timezone

from .models import Visit

logger = logging.getLogger(__name__)

EXCLUDED_PREFIXES = (
    "/admin/",
    "/static/",
    "/media/",
    "/api/",
    "/feed/",
    "/sitemap",
    "/robots",
    "/favicon",
)


class VisitorMiddleware:
    """A deliberately small, privacy-friendly daily visitor counter.

    We keep a salted hash of IP + user agent, never the raw address, and only
    one row per visitor per day. Failures never affect the response.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            self._record(request, response)
        except Exception:  # pragma: no cover - analytics must never break a page
            logger.debug("visitor tracking skipped", exc_info=True)
        return response

    def _record(self, request, response) -> None:
        if request.method != "GET":
            return
        if getattr(response, "status_code", 500) >= 400:
            return
        if not response.get("Content-Type", "").startswith("text/html"):
            return
        path = request.path
        if path.startswith(EXCLUDED_PREFIXES):
            return
        user_agent = request.META.get("HTTP_USER_AGENT", "")
        if any(bot in user_agent.lower() for bot in ("bot", "spider", "crawler", "preview")):
            return
        ip = request.META.get("REMOTE_ADDR", "0.0.0.0")
        raw = f"{ip}|{user_agent}|{settings.SECRET_KEY}".encode("utf-8")
        visitor_hash = hashlib.sha256(raw).hexdigest()[:32]
        try:
            Visit.objects.get_or_create(
                day=timezone.localdate(),
                visitor_hash=visitor_hash,
                defaults={"first_path": path[:255]},
            )
        except DatabaseError:
            logger.debug("visit table unavailable", exc_info=True)
