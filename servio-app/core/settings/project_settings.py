# project related settings

from core.url_names import AuthURLNames


# custom user model
AUTH_USER_MODEL = "accounts.AuthUser"

LOGIN_URL = AuthURLNames.LOGIN

LOCAL_APPS = [
    "accounts.apps.AccountsConfig",
]

LOCAL_MIDDLEWARES = []

