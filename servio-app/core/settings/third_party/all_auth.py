# django alluth settings
from core.url_names import AuthURLNames
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USERNAME_REQUIRED = False

# ACCOUNT_AUTHENTICATION_METHOD = "email"   # login via email
# ACCOUNT_EMAIL_REQUIRED = True
# ACCOUNT_UNIQUE_EMAIL = True
# ACCOUNT_USERNAME_REQUIRED = False
# ACCOUNT_USER_MODEL_USERNAME_FIELD = None

# ACCOUNT_EMAIL_VERIFICATION = "mandatory"  # or "optional" / "none"
# ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True
# LOGIN_REDIRECT_URL = "/"  # customize where user goes after login
# LOGOUT_REDIRECT_URL = "/"

ACCOUNT_SIGNUP_REDIRECT_URL = AuthURLNames.SIGNUP
ACCOUNT_LOGIN_REDIRECT_URL = AuthURLNames.LOGIN
ACCOUNT_LOGOUT_REDIRECT_URL = AuthURLNames.LOGIN


# url: https://docs.allauth.org/en/dev/account/configuration.html
ACCOUNT_EMAIL_VERIFICATION = "mandatory" # mandatory | optional | none
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*"] # ['username*', 'email', 'password1*', 'password2*']
ACCOUNT_LOGIN_BY_CODE_ENABLED = True # default is false
ACCOUNT_LOGIN_BY_CODE_TIMEOUT = 900 # 15mins
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_LOGIN_TIMEOUT = 1800 # 30mins

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': '123',
            'secret': '456',
            'key': ''
        }
    }
}