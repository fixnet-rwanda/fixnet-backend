import os
from .base import *  # noqa: F403

DEBUG = True

ALLOWED_HOSTS = ["*"]

# Database: use Postgres if specified, fallback to sqlite3 for local development/testing
if os.getenv("DATABASE_URL") or os.getenv("DB_NAME"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("DB_NAME", "fixnet_db"),
            "USER": os.getenv("DB_USER", "postgres"),
            "PASSWORD": os.getenv("DB_PASSWORD", "postgres"),
            "HOST": os.getenv("DB_HOST", "localhost"),
            "PORT": os.getenv("DB_PORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
        }
    }

# CORS
CORS_ALLOW_ALL_ORIGINS = True

# Cache: Local memory cache for quick development/testing if Redis is absent
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "fixnet-dev-cache",
    }
}
