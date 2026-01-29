from core.url_names import (
    AuthURLNames, BusinessURLS, CollaborationURLS,  EscrowURLS,
    NotificationsURLNames, OnboardingURLS, OppurtunitiesURLS,
    ProposalURLS, ReviewURLS, PaymentURLS,
)
from notifications.models.notification_channels import NotificationChannels
from accounts.models.profile import UserRole


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
        "ESCROW": EscrowURLS,
        "NOTIFICATION_URLS": NotificationsURLNames,
        "OPPURTUNITIES": OppurtunitiesURLS,
        "PAYMENT_URLS": PaymentURLS,
        "PROPOSALS": ProposalURLS,
        "REVIEWS": ReviewURLS,
        "USER_ONBOARDING_URLS": users_onboarding_urls,
        "UserRole": UserRole,
    }
