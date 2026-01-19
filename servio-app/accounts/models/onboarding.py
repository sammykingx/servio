from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


ONBOARDING_INTENT_CHOICES = {
    "book_services",
    "create_gigs",
    "collaborate",
}

def validate_onboarding_intents(value):
    """
    Ensures:
    - value is a list
    - values are strings
    - values are allowed
    """
    if not isinstance(value, list):
        raise ValidationError("Intent must be a list.")

    invalid = [
        v for v in value
        if not isinstance(v, str) or v not in ONBOARDING_INTENT_CHOICES
    ]

    if invalid:
        raise ValidationError(
            f"Invalid onboarding intents: {invalid}"
        )
        
class UserOnboardingIntent(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        to_field="email",
        on_delete=models.CASCADE,
        related_name="onboarding_intents"
    )
    intents = models.JSONField(
        validators=[validate_onboarding_intents],
        help_text="Validated onboarding intent payload"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "user_onboarding_intents"
    
    def save(self, *args, **kwargs):
        self.full_clean()  # ALWAYS validate
        super().save(*args, **kwargs)

