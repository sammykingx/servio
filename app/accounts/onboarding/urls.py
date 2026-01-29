from django.urls import include, path
from core.url_names import OnboardingURLS
from .users import urls as onboarding_users
from .providers import urls as onboarding_providers


urlpatterns = [
    path(
        "users/", include(onboarding_users, namespace=OnboardingURLS.Users.APP_NAME)  
    ),
    # path(
    #     "business/", include(onboarding_providers)  
    # ),
]