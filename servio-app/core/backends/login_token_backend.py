from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from accounts.models.user_tokens import UserToken, TokenType


class LoginTokenBackend(ModelBackend):
    """
    Authenticate a user using a token (e.g., magic link token).
    """
    
    _User = get_user_model()

    def authenticate(self, request, token=None):
        if token is None:
            raise ValueError("An authentication token needs to be provided")

        try:
            token_obj = UserToken.objects.get(token=token, token_type=TokenType.MAGIC_LINK)
        except UserToken.DoesNotExist:
            return None
        
        if not getattr(token_obj, "is_valid", False):
            return None

        token_obj.invalidate_token()
        

        return token_obj.user

