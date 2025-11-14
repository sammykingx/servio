# yourapp/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models import Q
from django.db.utils import IntegrityError
from django.utils.crypto import get_random_string
from datetime import timedelta


_TOKEN_LIFETIMES = {
    "email_verification": None,
    "password_reset": timedelta(minutes=20),
    "magic_link": None,
}

class TokenType(models.TextChoices):
    EMAIL_VERIFICATION = "email_verification", "Email Verification"
    PASSWORD_RESET = "password_reset", "Password Reset"
    MAGIC_LINK = "magic_link", "Magic Link"


class UserTokenManager(models.Manager):
    
    def generate_token(self, user, token_type: TokenType) -> tuple["UserToken", bool]:
        """
        Returns an existing valid token for the given token_type, or creates a new one.

        This method ensures that only one active token of a given type exists for a user
        at any time. If a valid, non-expired token already exists, it is returned and the
        second return value is False. Otherwise, a new token is generated, saved, and
        returned with the second return value set to True.

        Returns:
            tuple:
                (token_instance, created)
                - token_instance: The existing or newly created token object.
                - created (bool): True if a new token was created, False if an existing
                valid token was reused.

        Raises:
            IntegrityError: If a unique constraint is hit during token creation. In this
            case, the method falls back to returning the existing valid token.
        """
        now = timezone.now()
        lifetime = _TOKEN_LIFETIMES.get(token_type)
        queryset = self.filter(user=user, token_type=token_type, is_valid=True)
        
        if lifetime:
            queryset = queryset.filter(expires_at__gte=now)
        
        existing = queryset.first()
        
        if existing:
            return existing, False

        token = get_random_string(124).lower()

        try:
            return self.create(
                user=user,
                token=token,
                token_type=token_type,
                expires_at=now + lifetime if lifetime else None,
            ), True

        except IntegrityError:
            return self.get(
                user=user,
                token_type=token_type,
                is_valid=True,
            ), False


class UserToken(models.Model):
    """Model to store various user tokens for actions like
        password reset, email verification, etc.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tokens",
    )
    token = models.CharField(max_length=128, unique=True, db_index=True)
    token_type = models.CharField(max_length=50, choices=TokenType.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True)
    used_at = models.DateTimeField(null=True)
    is_valid = models.BooleanField(default=True)
    
    
    objects = UserTokenManager()
    

    class Meta:
        db_table = "user_tokens"
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["token", "token_type"],
                name="usertoken_tokentype_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "token_type"],
                condition=Q(is_valid=True),
                name="unique_active_token_per_user_type",
            )
        ]


    def __str__(self):
        return f"{self.user.email} - {self.token_type}"

    def has_expired(self) -> bool:
        return self.is_valid

    def invalidate_token(self):
        self.is_valid = False
        self.used_at = timezone.now()
        self.save(update_fields=["is_valid", "used_at"])
