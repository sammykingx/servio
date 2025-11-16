from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import AbstractUser
from accounts.models.user_tokens import UserToken, TokenType
from typing import Union


class MagicLinkBackend(ModelBackend):
    """
    Authenticate a user using a token (e.g., magic link token).
    """

    def authenticate(self, request, token) -> Union[AbstractUser, None]:
        try:
            token_obj = UserToken.objects.get(token=token, token_type=TokenType.MAGIC_LINK)
        except UserToken.DoesNotExist:
            return None

        if not getattr(token_obj, "is_valid", False):
            return None
        
        token_obj.invalidate_token()

        return token_obj.user

