THIRD_PARTY_APPS = [
    # "django_extensions",
    # "allauth",
    # "allauth.account",
    # "allauth.socialaccount",
    "django_htmx",
    "django_zxcvbn_password_validator",
]

THIRD_PARTY_MIDDLEWARES = [
    # "allauth.account.middleware.AccountMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
]

from .all_auth import *
from .firebase import *
