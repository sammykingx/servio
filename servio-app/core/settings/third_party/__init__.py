THIRD_PARTY_APPS = [
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
]

THIRD_PARTY_MIDDLEWARES = [
    "allauth.account.middleware.AccountMiddleware",
]

from .all_auth import *