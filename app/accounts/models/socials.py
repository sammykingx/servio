from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class Platform(models.TextChoices):
    FACEBOOK = "facebook", "Facebook"
    INSTAGRAM = "instagram", "Instagram"
    TWITTER = "twitter", "Twitter"
    LINKEDIN = "linkedin", "LinkedIn"
    # YOUTUBE = "youtube", "YouTube"
    # TIKTOK = "tiktok", "TikTok"
    # GITHUB = "github", "GitHub"
    # OTHER = "other", "Other"


class SocialLink(models.Model):
    """
    Stores social media links associated with a user.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        to_field="email",
        on_delete=models.CASCADE,
        related_name="social_links",
        blank=True,
        null=True,
    )
    business = models.ForeignKey(
        "business_accounts.BusinessAccount",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="social_links",
    )
    platform = models.CharField(max_length=30, choices=Platform.choices)
    url = models.URLField(max_length=250)

    class Meta:
        db_table = "social_links"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "platform"],
                name="unique_user_social_platform",
            ),
            models.UniqueConstraint(
                fields=["business", "platform"],
                condition=models.Q(business__isnull=False),
                name="unique_business_social_platform",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(user__isnull=False, business__isnull=True)
                    | models.Q(user__isnull=True, business__isnull=False)
                ),
                name="social_link_scope_check",
            ),
        ]
        
    def clean(self):
        if not self.user and not self.business:
            raise ValidationError(
                "Either 'user' or 'business' must be set."
            )

        if self.user and self.business:
            raise ValidationError(
                "Only one of 'user' or 'business' may be set."
            )

        if not self.platform:
            raise ValidationError("Platform is required.")

        if not self.url:
            raise ValidationError("URL is required.")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
