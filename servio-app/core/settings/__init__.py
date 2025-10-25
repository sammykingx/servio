from .django_base_settings import *
from .third_party import *
from .project_apps import *
from .env.development import *
from .email_config import *

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS
MIDDLEWARE = DJANGO_MIDDLEWARE + THIRD_PARTY_MIDDLEWARES + LOCAL_MIDDLEWARES