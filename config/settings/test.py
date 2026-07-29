"""Automated test settings."""
from copy import deepcopy

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403

SECRET_KEY = "test-only-insecure-placeholder"
DEBUG = False
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]

DATABASES = deepcopy(DATABASES)  # noqa: F405

TEST_DATABASE_NAME = env(  # noqa: F405
    "TEST_DATABASE_NAME",
    default="test_social_commerce",
)
if not TEST_DATABASE_NAME:
    raise ImproperlyConfigured("TEST_DATABASE_NAME cannot be empty.")
if TEST_DATABASE_NAME == DATABASES["default"]["NAME"]:  # noqa: F405
    raise ImproperlyConfigured(
        "TEST_DATABASE_NAME must differ from the development database name."
    )

DATABASES["default"]["TEST"] = {"NAME": TEST_DATABASE_NAME}  # noqa: F405
