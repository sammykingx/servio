# Email configuration settings
from decouple import config

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST", default=None)
EMAIL_PORT = config("EMAIL_PORT", default=465, cast=int)
EMAIL_USE_SSL = config("USE_SSL", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_USERNAME")
EMAIL_HOST_PASSWORD = config("EMAIL_PASSWORD")
