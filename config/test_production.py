"""Isolated production configuration and deployable asset checks."""
import os
from pathlib import Path
import runpy
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.conf import settings
from django.core.checks import Tags, run_checks
from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command
from django.contrib.staticfiles.storage import staticfiles_storage
from django.test import SimpleTestCase, override_settings


class ProductionSettingsTests(SimpleTestCase):
    def load_settings(self, **changes):
        environment = {
            "DJANGO_SECRET_KEY": "production-test-only-0123456789-abcdefghijklmnopqrstuvwxyz",
            "DATABASE_URL": "postgres://example:example@localhost/example",
            "DJANGO_ALLOWED_HOSTS": "seller.example.com",
            "DJANGO_CSRF_TRUSTED_ORIGINS": "https://seller.example.com",
        }
        environment.update(changes)
        with patch.dict(os.environ, environment, clear=True):
            return runpy.run_module("config.settings.production")

    def test_required_configuration_fails_closed(self):
        for name in ("DJANGO_SECRET_KEY", "DATABASE_URL", "DJANGO_ALLOWED_HOSTS"):
            with self.subTest(name=name), self.assertRaises(ImproperlyConfigured):
                self.load_settings(**{name: ""})

    def test_unsafe_configuration_is_rejected(self):
        cases = (
            {"DJANGO_SECRET_KEY": "change-me-in-local-development"},
            {"DJANGO_SECRET_KEY": "x" * 60},
            {"DJANGO_DEBUG": "True"},
            {"DJANGO_ALLOWED_HOSTS": "*"},
            {"DJANGO_ALLOWED_HOSTS": "https://seller.example.com"},
            {"DJANGO_ALLOWED_HOSTS": "seller example.com"},
            {"DJANGO_ALLOWED_HOSTS": ".example.com"},
            {"DJANGO_ALLOWED_HOSTS": "seller.example.com:443"},
            {"DJANGO_ALLOWED_HOSTS": "[broken]"},
            {"DATABASE_URL": "sqlite:///db.sqlite3"},
            {"DJANGO_CSRF_TRUSTED_ORIGINS": "http://seller.example.com"},
            {"DJANGO_CSRF_TRUSTED_ORIGINS": "https://*.example.com"},
            {"DJANGO_CSRF_TRUSTED_ORIGINS": "https://seller.example.com/path"},
            {"DJANGO_CSRF_TRUSTED_ORIGINS": "https://user@seller.example.com"},
            {"DJANGO_CSRF_TRUSTED_ORIGINS": "https://seller.example.com:wrong"},
            {"DJANGO_CSRF_TRUSTED_ORIGINS": "https://seller.example.com:70000"},
            {"DJANGO_CSRF_TRUSTED_ORIGINS": "https://seller.example.com:"},
            {"DJANGO_CSRF_TRUSTED_ORIGINS": "https://[broken"},
            {"DJANGO_MEDIA_ROOT": "media"},
            {"DJANGO_MEDIA_ROOT": str(settings.BASE_DIR / "staticfiles" / "uploads")},
            {"DJANGO_MEDIA_ROOT": str(settings.BASE_DIR / "static")},
            {"DJANGO_MEDIA_ROOT": str(settings.BASE_DIR / "static" / "uploads")},
            {"DJANGO_MEDIA_ROOT": str(settings.BASE_DIR)},
        )
        for values in cases:
            with self.subTest(values=values), self.assertRaises(ImproperlyConfigured):
                self.load_settings(**values)

    def test_explicit_hosts_and_https_origins_accept_ports_and_ipv6(self):
        production = self.load_settings(
            DJANGO_ALLOWED_HOSTS="seller.example.com,localhost,127.0.0.1,[::1]",
            DJANGO_CSRF_TRUSTED_ORIGINS="https://seller.example.com:8443,https://[::1]:8443,https://[::1]",
        )
        self.assertEqual(len(production["ALLOWED_HOSTS"]), 4)
        self.assertEqual(len(production["CSRF_TRUSTED_ORIGINS"]), 3)

    def test_https_and_postgres_production_defaults(self):
        production = self.load_settings(DJANGO_CSRF_TRUSTED_ORIGINS="")
        self.assertFalse(production["DEBUG"])
        self.assertEqual(production["ALLOWED_HOSTS"], ["seller.example.com"])
        self.assertEqual(production["CSRF_TRUSTED_ORIGINS"], [])
        self.assertEqual(production["DATABASES"]["default"]["ENGINE"], "django.db.backends.postgresql")
        for name in ("SESSION_COOKIE_SECURE", "CSRF_COOKIE_SECURE", "SECURE_SSL_REDIRECT"):
            self.assertTrue(production[name])
        security_settings = {
            name: production[name] for name in (
                "SECRET_KEY", "DEBUG", "ALLOWED_HOSTS", "SESSION_COOKIE_SECURE",
                "CSRF_COOKIE_SECURE", "SECURE_SSL_REDIRECT", "SECURE_HSTS_SECONDS",
                "SECURE_HSTS_INCLUDE_SUBDOMAINS", "SECURE_HSTS_PRELOAD",
            )
        }
        with override_settings(**security_settings):
            findings = run_checks(tags=[Tags.security], include_deployment_checks=True)
        # Domain-wide HSTS and browser preload are hosting-stage decisions.
        self.assertEqual(
            [finding.id for finding in findings if finding.id not in {"security.W005", "security.W021"}],
            [],
        )

    def test_production_assets_collect_and_resolve_without_a_cdn(self):
        production = self.load_settings()
        scratch = settings.BASE_DIR / ".local"
        scratch.mkdir(exist_ok=True)
        with TemporaryDirectory(dir=scratch) as directory:
            with override_settings(STORAGES=production["STORAGES"], STATIC_ROOT=directory, DEBUG=False):
                call_command("collectstatic", interactive=False, verbosity=0)
                for asset in ("css/app.css", "js/product_workspace.js", "django_htmx/htmx-2.min.js"):
                    with self.subTest(asset=asset):
                        hashed_name = staticfiles_storage.stored_name(asset)
                        self.assertNotEqual(asset, hashed_name)
                        self.assertTrue((Path(directory) / hashed_name).is_file())
                        self.assertIn(hashed_name, staticfiles_storage.url(asset))
                self.assertTrue((Path(directory) / "staticfiles.json").is_file())
