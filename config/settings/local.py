"""Local development settings."""
from .base import *  # noqa: F403

SECRET_KEY = env(  # noqa: F405
    "DJANGO_SECRET_KEY",
    default="dev-only-insecure-placeholder-change-me",
)
DEBUG = env.bool("DJANGO_DEBUG", default=True)  # noqa: F405
ALLOWED_HOSTS = env.list(  # noqa: F405
    "DJANGO_ALLOWED_HOSTS",
    default=["localhost", "127.0.0.1"],
)
