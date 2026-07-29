"""Automated test settings."""
from .base import *  # noqa: F403

SECRET_KEY = "test-only-insecure-placeholder"
DEBUG = False
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]
