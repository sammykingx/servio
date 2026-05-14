from django.db import models
from django.conf import settings
from django.utils.text import slugify
from uuid6 import uuid7
from nanoid import generate
from autoslug import AutoSlugField


def generate_business_id():
    seed = "23456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    return "SB-" + generate(seed, 12)


class BusinessAccount(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)

    business_id = models.CharField(
        max_length=20,
        default=generate_business_id,
        unique=True,
        editable=False,
        db_index=True,
    )

    slug = models.SlugField(
        max_length=120,
        unique=True,
        db_index=True,
        null=True,
        blank=True,
    )

    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="business_account",
    )

    business_name = models.CharField(max_length=255)
    tagline = models.CharField(max_length=255, blank=True, null=True)
    business_email = models.EmailField()
    business_phone = models.CharField(max_length=30)
    industry = models.CharField(max_length=70, null=True)
    niche = models.CharField(blank=True, null=True, max_length=70)
    bio = models.TextField(blank=True)
    logo_url = models.ImageField(
        upload_to="businesses/logos", null=True, blank=True
    )

    address = models.ForeignKey(
        "accounts.Address",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="businesses",
    )
    
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_restricted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "business_account"
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["business_id"]),
        ]

    def __str__(self):
        return f"(ID: {self.business_id}, Name: {self.business_name})"
