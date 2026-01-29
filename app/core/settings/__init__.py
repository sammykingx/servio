from .django_base_settings import *
from .third_party import *
from .project_settings import *
from .email_config import *
from decouple import config


if config("ENVIRONMENT") == "production":
    from .env.production import *
else:
    from .env.development import *


INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS
MIDDLEWARE = (
    DJANGO_MIDDLEWARE + THIRD_PARTY_MIDDLEWARES + LOCAL_MIDDLEWARES
)
# Used by default session engine
# SESSION_ENGINE = "django.contrib.sessions.backends.db"

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "verbose": {
            "format": (
                "[{asctime}] {levelname} "
                "{name}:{lineno} "
                "{message}"
            ),
            "style": "{",
        },
        "simple": {
            "format": "[{levelname}] {message}",
            "style": "{",
        },
    },

    "handlers": {
        # -------------------
        # DB ERRORS
        # -------------------
        "db_file": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "maxBytes": 1024 * 1024 * 20,
            "backupCount": 5,
            "filename": LOG_DIR / "db.log",
            "formatter": "verbose",
            "encoding": "utf-8",
            "delay": True,
        },

        # -------------------
        # GENERAL APP ERRORS
        # -------------------
        "app_file": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "maxBytes": 1024 * 1024 * 20,
            "backupCount": 5,
            "filename": LOG_DIR / "django.log",
            "formatter": "verbose",
            "encoding": "utf-8",
            "delay": True,
        },

        # -------------------
        # CONSOLE / PASSENGER
        # -------------------
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },

    "loggers": {
        # MySQL / ORM issues
        "django.db.backends": {
            "handlers": ["db_file"],
            "level": "ERROR",
            "propagate": False,
        },

        # Django internal errors
        "django": {
            "handlers": ["app_file", "console"],
            "level": "ERROR",
            "propagate": True,
        },
    },
    
     # Everything else
    "root": {
        "handlers": ["app_file", "console"],
        "level": "ERROR",
    },
}


