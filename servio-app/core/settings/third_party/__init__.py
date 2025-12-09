THIRD_PARTY_APPS = [
    "django_extensions",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
]

THIRD_PARTY_MIDDLEWARES = [
    "allauth.account.middleware.AccountMiddleware",
]

from .all_auth import *
