"""Production-safe settings.

These settings validate required environment variables without selecting a
hosting provider or embedding real secrets.
"""
from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403


def require_env(name: str) -> str:
    """Return a required environment value or fail during Django startup."""
    value = env(name, default="")  # noqa: F405
    if not value:
        raise ImproperlyConfigured(f"{name} is required in production settings.")
    return value


SECRET_KEY = require_env("DJANGO_SECRET_KEY")
DEBUG = env.bool("DJANGO_DEBUG", default=False)  # noqa: F405
if DEBUG:
    raise ImproperlyConfigured("DJANGO_DEBUG must be false in production settings.")

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[])  # noqa: F405
if not ALLOWED_HOSTS:
    raise ImproperlyConfigured(
        "DJANGO_ALLOWED_HOSTS is required in production settings."
    )

DATABASES = {
    "default": postgres_database_config(  # noqa: F405
        require_env("DATABASE_URL"),
        "DATABASE_URL",
    )
}
