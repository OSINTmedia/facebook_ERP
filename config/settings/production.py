"""Production-safe settings.

These settings validate required environment variables without selecting a
hosting provider or embedding real secrets.
"""
from ipaddress import ip_address
import re
from urllib.parse import urlsplit

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403


def require_env(name: str) -> str:
    """Return a required environment value or fail during Django startup."""
    value = env(name, default="")  # noqa: F405
    if not value.strip():
        raise ImproperlyConfigured(f"{name} is required in production settings.")
    return value


SECRET_KEY = require_env("DJANGO_SECRET_KEY")
if len(SECRET_KEY) < 50 or len(set(SECRET_KEY)) < 5 or SECRET_KEY.startswith("django-insecure-"):
    raise ImproperlyConfigured("DJANGO_SECRET_KEY must be a strong production secret.")
DEBUG = env.bool("DJANGO_DEBUG", default=False)  # noqa: F405
if DEBUG:
    raise ImproperlyConfigured("DJANGO_DEBUG must be false in production settings.")

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[])  # noqa: F405
if not ALLOWED_HOSTS:
    raise ImproperlyConfigured(
        "DJANGO_ALLOWED_HOSTS is required in production settings."
    )
def is_explicit_host(host):
    if host.startswith("[") and host.endswith("]"):
        try:
            return ip_address(host[1:-1]).version == 6
        except ValueError:
            return False
    return len(host) <= 253 and all(
        re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?", label)
        for label in host.split(".")
    )


if not all(is_explicit_host(host) for host in ALLOWED_HOSTS):
    raise ImproperlyConfigured("DJANGO_ALLOWED_HOSTS must contain explicit host names.")

CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])  # noqa: F405
for origin in CSRF_TRUSTED_ORIGINS:
    try:
        parsed = urlsplit(origin)
        port = parsed.port
    except ValueError as exc:
        raise ImproperlyConfigured("CSRF trusted origins must be explicit HTTPS origins.") from exc
    if (
        parsed.scheme != "https" or not parsed.hostname or "*" in origin
        or not is_explicit_host(parsed.netloc.rsplit(":", 1)[0] if port is not None else parsed.netloc)
        or parsed.netloc.endswith(":")
        or parsed.username is not None or parsed.password is not None
        or parsed.path or parsed.query or parsed.fragment
        or any(character.isspace() for character in origin)
    ):
        raise ImproperlyConfigured("CSRF trusted origins must be explicit HTTPS origins.")

# Same-origin HTTPS requests need no CSRF trusted-origin exception. Add only
# deliberate cross-origin exceptions; do not trust forwarded headers by default.
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 3600
# Subdomain and preload policy requires knowledge of the eventual hosted domain.
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# Collect immutable, fingerprinted assets for the host's static-file server.
# Product media stays private and is served by the authenticated media view;
# the host must mount persistent storage here, never a public media directory.
STATIC_ROOT = BASE_DIR / "staticfiles"  # noqa: F405
MEDIA_ROOT = Path(env("DJANGO_MEDIA_ROOT", default=str(BASE_DIR / "media")))  # noqa: F405
public_static_roots = [STATIC_ROOT, *STATICFILES_DIRS]  # noqa: F405
if not MEDIA_ROOT.is_absolute() or any(
    MEDIA_ROOT.resolve() == Path(root).resolve()
    or MEDIA_ROOT.resolve() in Path(root).resolve().parents
    or Path(root).resolve() in MEDIA_ROOT.resolve().parents
    for root in public_static_roots
):
    raise ImproperlyConfigured("DJANGO_MEDIA_ROOT must be absolute and separate from static files.")
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
    },
}

DATABASES = {
    "default": postgres_database_config(  # noqa: F405
        require_env("DATABASE_URL"),
        "DATABASE_URL",
    )
}
