from core.url_names import AuthURLNames, NotificationsURLNames
from notifications.models.notification_channels import NotificationChannels


def app_urlnames(request):
    # lazily creating notifications with defaults
    # if not present in model
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
        "NOTIFICATION_URLS": NotificationsURLNames,
    }
