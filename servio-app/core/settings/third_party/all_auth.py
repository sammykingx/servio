# django alluth settings
from core.url_names import AuthURLNames
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# LOGIN_REDIRECT_URL = "/"  # customize where user goes after login
# LOGOUT_REDIRECT_URL = AuthURLNames.LOGIN

# NOT IN DOCS SO I DON'T THINK IT'S REQUIRED
# ACCOUNT_SIGNUP_REDIRECT_URL = AuthURLNames.EMAIL_VERIFICATION_SENT # view that renders, verify email if not social auth
# ACCOUNT_LOGIN_REDIRECT_URL = AuthURLNames.ACCOUNT_DASHBOARD
# ACCOUNT_LOGOUT_REDIRECT_URL = AuthURLNames.LOGIN


# SIGN UP CONFIG SETTINGS
# url: https://docs.allauth.org/en/dev/account/configuration.html
# url 2: using custom user model https://docs.allauth.org/en/dev/account/advanced.html
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*"]
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_FORMS = {"signup": "accounts.forms.UserSignupForm"}
ACCOUNT_ADAPTER = "accounts.adapters.CustomAccountAdapter"
ACCOUNT_EMAIL_SUBJECT_PREFIX = "Servio - "

# EMAIL VERIFICATION SETTINGS
# url: https://docs.allauth.org/en/dev/account/configuration.html#email-verification
ACCOUNT_EMAIL_VERIFICATION = "mandatory" # mandatory | optional | none
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 2

# LOGIN CONFIG SETTINGS
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