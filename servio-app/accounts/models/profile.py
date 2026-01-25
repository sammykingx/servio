from django.apps import apps
from django.conf import settings
from django.db import models, transaction
from django.core.exceptions import ValidationError


class UserRole(models.TextChoices):
    MEMBERS = "member", "Members"
    PROVIDERS = "provider", "Providers"
    ADMIN = "admin", "Admin" # not used
    STAFF = "staff", "Staff" # not used


class UserProfile(models.Model):
    """
    Extended profile for AuthUser (One-to-One relationship).
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        to_field="email",
        on_delete=models.CASCADE,
        related_name="profile",
    )
    
    mobile_num = models.CharField(
        max_length=18, unique=True, blank=True, null=True
    )
    
    alt_mobile_num = models.CharField(
        max_length=20, blank=True, null=True
    )
    
    industry = models.ForeignKey(
        "collaboration.GigCategory",
        on_delete=models.SET_NULL,
        related_name="user_profiles",
        null=True,
        blank=True,
        limit_choices_to={"parent__isnull": True},
        help_text="Primary industry (top-level category)",
    )

    niches = models.ManyToManyField(
        "collaboration.GigCategory",
        related_name="profiles_niches",
        blank=True,
        limit_choices_to={"parent__isnull": False},
        help_text="Selected niches (subcategories under industry)",
    )

    bio = models.TextField(
        max_length=600,
        blank=True,
        help_text="Professional bio shown on public profile",
    )
    
    avatar_url = models.ImageField(
        upload_to="avatars/", null=True, blank=True
    )
    
    date_of_birth = models.DateField(blank=True, null=True)
    is_business_owner = models.BooleanField(default=False)
    
    role = models.CharField(
        choices=UserRole.choices,
        default=UserRole.MEMBERS,
    )

    class Meta:
        db_table = "user_profiles"
