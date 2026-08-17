"""Shared Django settings for all environments."""
from pathlib import Path
from urllib.parse import urlparse

from django.core.exceptions import ImproperlyConfigured
import environ

BASE_DIR = Path(__file__).resolve().parents[2]

env = environ.Env()

POSTGRES_DATABASE_SCHEMES = {"postgres", "postgresql"}


def postgres_database_config(database_url: str, setting_name: str) -> dict:
    """Parse a PostgreSQL database URL and reject non-PostgreSQL fallbacks."""
    scheme = urlparse(database_url).scheme
    if scheme not in POSTGRES_DATABASE_SCHEMES:
        raise ImproperlyConfigured(f"{setting_name} must use a PostgreSQL URL.")
    return environ.Env.db_url_config(database_url)

env_file = BASE_DIR / ".env"
if env_file.exists():
    environ.Env.read_env(env_file)

INSTALLED_APPS = [
    "accounts",
    "businesses",
    "catalog",
    "django_htmx",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
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
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": postgres_database_config(
        env("DATABASE_URL"),
        "DATABASE_URL",
    )
}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "accounts.User"
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "shell_home"
LOGOUT_REDIRECT_URL = "accounts:login"

DEMO_ACCESS_ENABLED = env.bool("DEMO_ACCESS_ENABLED", default=False)
DEMO_USER_EMAIL = env("DEMO_USER_EMAIL", default="")
DEMO_USER_PASSWORD = env("DEMO_USER_PASSWORD", default="")

CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])
