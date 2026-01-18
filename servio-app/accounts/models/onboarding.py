from django.db import models
from django.conf import settings


class OnboardingIntent(models.Model):
    """
    Canonical list of onboarding intents.
    """
    key = models.SlugField(unique=True)
    label = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "onboarding_intents"

    def __str__(self):
        return self.label


class UserOnboardingIntent(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="onboarding_intents"
    )
    intent = models.ForeignKey(
        OnboardingIntent,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "intent")
        db_table = "user_onboarding_intents"

