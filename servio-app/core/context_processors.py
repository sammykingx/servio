from core.url_names import AuthURLNames, BusinessURLS, NotificationsURLNames
from notifications.models.notification_channels import NotificationChannels
from accounts.models.profile import UserRole


def app_urlnames(request):
    # lazily creating notifications with defaults
    # if not present in model
    if request.user.is_authenticated:
        channels, created = NotificationChannels.objects.get_or_create(
                user=request.user,
                defaults={
                    "in_app": True,
                    "email": True,
                    "web_push": False,
                    "sms": False,
                    "whatsapp": False,
                }
            )
    
    return {
        "AUTH_URLS": AuthURLNames,
        "BIZ_URLS": BusinessURLS,
        "NOTIFICATION_URLS": NotificationsURLNames,
        "UserRole": UserRole,
    }
