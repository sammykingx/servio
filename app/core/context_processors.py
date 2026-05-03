from core.url_names import (
    AuthURLNames, BusinessURLS, CollaborationURLS,  SmartReleaseURLS,
    NotificationsURLNames, OnboardingURLS, OppurtunitiesURLS,
    ProposalURLS, ReviewURLS, PaymentURLS,
)
from notifications.models.notification_channels import NotificationChannels
from accounts.models.profile import UserRole
from constants import APP_SUBSCRIPTION_FEE, USD_TO_NGN_RATE


class NamespacedURLs:
    """
    Static helper to transform local URL names into namespaced ones.
    """

    @staticmethod
    def transform(app_name, urls_dict):
        """
        Returns an object with attributes for each URL, fully namespaced.
        """
        class URLContainer:
            pass

        container = URLContainer()
        for key, value in urls_dict.items():
            setattr(container, key, f"{app_name}:{value}")

        return container


def app_urlnames(request): 
    users_onboarding_urls = NamespacedURLs.transform(
        OnboardingURLS.Users.APP_NAME,
        {
            "WELCOME": OnboardingURLS.Users.WELCOME,
            "PROFILE_SETUP": OnboardingURLS.Users.PROFILE_SETUP,
            "EXPERTISE_AND_NICHE": OnboardingURLS.Users.EXPERTISE_AND_NICHE,
            "OBJECTIVES": OnboardingURLS.Users.OBJECTIVES,
            "COMPLETE": OnboardingURLS.Users.COMPLETE,
        }
    )
    
    return {
        "AUTH_URLS": AuthURLNames,
        "BIZ_URLS": BusinessURLS,
        "COLLABORATION_URLS": CollaborationURLS,
        "SMART_RELEASE": SmartReleaseURLS,
        "NOTIFICATION_URLS": NotificationsURLNames,
        "OPPURTUNITIES": OppurtunitiesURLS,
        "PAYMENT_URLS": PaymentURLS,
        "PROPOSALS": ProposalURLS,
        "REVIEWS": ReviewURLS,
        "USER_ONBOARDING_URLS": users_onboarding_urls,
        "UserRole": UserRole,
        "SUBSCRIPTION_FEE": APP_SUBSCRIPTION_FEE,
        "NGN_SUBSCRIPTION_FEE": APP_SUBSCRIPTION_FEE * USD_TO_NGN_RATE,
    }

def firebase_settings(request):
    from django.conf import settings
    
    return {
        "FIREBASE_VAPID_KEY": settings.FIREBASE_VAPID_KEY,
        "FIREBASE_CONFIG": {
            "apiKey": settings.FIREBASE_API_KEY,
            "authDomain": settings.FIREBASE_AUTH_DOMAIN,
            "projectId": settings.FIREBASE_PROJECT_ID,
            "storageBucket": settings.FIREBASE_STORAGE_BUCKET,
            "messagingSenderId": settings.FIREBASE_STORAGE_BUCKET,
            "appId": settings.FIREBASE_APP_ID,
            "measurementId": settings.FIREBASE_MEASUREMENT_ID,
        }
    }
    