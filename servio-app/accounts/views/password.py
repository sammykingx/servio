from django.contrib.auth.views import (
    PasswordResetDoneView,
    PasswordChangeView,
    PasswordChangeDoneView,
)
from django.views import View
from django.shortcuts import render
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse, HttpRequest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from services.email_service import EmailService
from accounts.models.user_tokens import UserToken, TokenType
from core.url_names import AuthURLNames
from template_map.accounts import Accounts
from template_map.emails import AccountMails
from typing import Union
from loggers import default_logger as logger


class PasswordResetEmailView(View):
    """
    Allows a user to reset their password by generating a
    one-time use link that can be used to reset the password,
    and sending that link to the user’s registered email address.
    """
    http_method_names = ["get", "post"]
    _user_model:AbstractUser = get_user_model()
    
    def get(self, request, *args, **kwargs) -> HttpResponse:
        return render(request, Accounts.Auth.REQUEST_PASSWORD_RESET)
    
    def post(self, request: HttpRequest, *args, **kwargs) -> Union[HttpResponse, JsonResponse]:
        email = self.request.POST.get("email")
        user = self.fetch_user(email)
        if user:
            token = UserToken.objects.generate_token(
                user=user,
                token_type=TokenType.PASSWORD_RESET,
            ).token
            self.send_reset_link(user, token)
            
        return render(request, Accounts.Auth.REQUEST_PASSWORD_RESET)
        
        
    def fetch_user(self, email) ->Union[AbstractUser, None]:
        try:
            user = self._user_model.objects.get(email=email)
        except self._user_model.DoesNotExist:
            return None
        return user
    
    def send_reset_link(self, user:AbstractUser, token:str) -> bool:
        """
        Send reset link to user
        """
        if not user.is_verified:
            return False
        
        login_url = self.request.build_absolute_uri(
            reverse_lazy(
                AuthURLNames.PASSWORD_RESET,
                kwargs={"token": token}
            )
        )
        
        context = {
            "host": self.request.build_absolute_uri("/"),
            "reset_url": login_url,
        }
        
        EmailService(user.email) \
            .set_subject(AccountMails.Subjects.PASSWORD_RESET) \
            .use_template(AccountMails.PASSWORD_RESET) \
            .with_context(**context) \
            .send()
            
        return True

    
class NewPasswordView(View):
    """
        Used when a user is not logged in and wants to reset password
        using reset link sent to tmail address
    """
    http_method_names = {"get", "post"}
    
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        context = {"token" : kwargs.get("token")}
        return render(request, Accounts.Auth.PASSWORD_RESET, context)
    
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        context = {"token" : kwargs.get("token")}
        data = self.request.POST.dict()
        logger.info(data)
        return render(request, Accounts.Auth.PASSWORD_RESET, context)


class PasswordResetEmailDOneView(PasswordResetDoneView):
    """
    The page shown after a user has been emailed a link to
    reset their password.
    """
    
    pass


class ChangePasswordView(PasswordChangeView):
    """Allows a user to change their password."""
    
    # Used when the logged-in user wants to change their own password
    # Key characteristics:
    #   - User must be authenticated
    #   - User must know their current password
    #   - Typical use: “Change Password” inside user settings
    #   - Does not involve email or tokens
    
    # User is logged in
    # They go to /accounts/password/change/
    # They enter:
    #   current password
    #   new password
    #   confirm password
    # Password changes immediately
    # User stays logged in (unless configured otherwise)
    
    pass


class ChangePasswordCompleteView(PasswordChangeDoneView):
    """The page shown after a user has changed their password."""
    
    pass
    