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


class WebPushDeviceToken(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        to_field="email",
        related_name="web_push_tokens"
    )

    token = models.TextField(unique=True)
    user_agent = models.TextField()
    platform = models.CharField(max_length=20)
    browser = models.CharField(max_length=20)
    device = models.CharField(max_length=15)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "web_push_device_tokens"
        indexes = [
            models.Index(fields=["user", "is_active"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'token'], 
                name='unique_user_device_token'
            )
        ]
        
    def deactivate(self):
        self.is_active = False
        self.save(update_fields=["is_active"])
