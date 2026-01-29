from django.db import models
from django.conf import settings


class NotificationChannels(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_channels"
    )
    
    in_app = models.BooleanField(default=True)
    email = models.BooleanField(default=True)
    web_push = models.BooleanField(default=False)
    sms = models.BooleanField(default=False)
    whatsapp = models.BooleanField(default=False)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "notification_channels"

    def __str__(self):
        channel_map = {
            "In-App": self.in_app,
            "Email": self.email,
            "Web Push": self.web_push,
            "SMS": self.sms,
            "Whatsapp": self.whatsapp,
        }

        enabled = [name for name, enabled in channel_map.items() if enabled]

        return f"{self.user.email} -> {', '.join(enabled) or 'No channels'}"

