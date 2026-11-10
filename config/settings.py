"""Django settings for IR 之下."""
from __future__ import annotations

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
VENDOR_DIR = BASE_DIR / "vendor"
if VENDOR_DIR.is_dir():
    sys.path.insert(0, str(VENDOR_DIR))


def _load_dotenv(path: Path) -> None:
    """A tiny .env loader so the project has no extra runtime dependency."""
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


_load_dotenv(BASE_DIR / ".env")


def env_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).lower() in {"1", "true", "yes", "on"}


def env_list(name: str, default: str = "") -> list[str]:
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


SECRET_KEY = os.getenv(
    "BLOG_SECRET_KEY",
    "dev-only-ir-notes-7f1c4d3e9b2a6c8f5d0e1a4b7c9d2e3f-change-me-in-production",
)
DEBUG = env_bool("BLOG_DEBUG", True)
ALLOWED_HOSTS = env_list("BLOG_ALLOWED_HOSTS", "127.0.0.1,localhost,[::1],testserver")
CSRF_TRUSTED_ORIGINS = env_list("BLOG_CSRF_TRUSTED_ORIGINS")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "blog",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "blog.middleware.VisitorMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "blog.context_processors.site_context",
                "blog.context_processors.giscus_context",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
        "OPTIONS": {"timeout": 20},
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "zh-hans"
TIME_ZONE = "Asia/Shanghai"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
X_FRAME_OPTIONS = "DENY"
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

SITE_URL = os.getenv("BLOG_SITE_URL", "http://127.0.0.1:8000").rstrip("/")
SITE_ID = 1

GISCUS = {
    "repo": os.getenv("BLOG_GISCUS_REPO", ""),
    "repo_id": os.getenv("BLOG_GISCUS_REPO_ID", ""),
    "category": os.getenv("BLOG_GISCUS_CATEGORY", "Announcements"),
    "category_id": os.getenv("BLOG_GISCUS_CATEGORY_ID", ""),
    "mapping": "pathname",
    "strict": "0",
    "reactions_enabled": "1",
    "emit_metadata": "0",
    "input_position": "top",
    "lang": "zh-CN",
}

# Set BLOG_DEMO_MODE=0 to disable demo-specific copy and links.
DEMO_MODE = env_bool("BLOG_DEMO_MODE", True)

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

SECURE_HSTS_SECONDS = int(os.getenv("BLOG_HSTS_SECONDS", "0"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("BLOG_HSTS_INCLUDE_SUBDOMAINS", False)
SECURE_HSTS_PRELOAD = env_bool("BLOG_HSTS_PRELOAD", False)
SECURE_SSL_REDIRECT = env_bool("BLOG_SSL_REDIRECT", False)

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = env_bool("BLOG_SECURE_COOKIES", True)
    CSRF_COOKIE_SECURE = env_bool("BLOG_SECURE_COOKIES", True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": os.getenv("BLOG_LOG_LEVEL", "INFO")},
}
