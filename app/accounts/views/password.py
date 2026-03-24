from django.db import transaction
from django.views import View
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.password_validation import validate_password
from services.email_service import EmailService
from accounts.models.user_tokens import UserToken, TokenType
from accounts.schemas import PasswordChangeSchema
from core.url_names import AuthURLNames
from template_map.accounts import Accounts
from template_map.emails import AccountMails
from pydantic import ValidationError as PydanticError
from typing import Optional, Union
from loggers import default_logger as logger


class PasswordResetEmailView(View):
    """
    Allows a user to reset their password by generating a
    one-time use link that can be used to reset the password,
    and sending that link to the user’s registered email address.
    """

    http_method_names = ["get", "post"]
    _user_model: AbstractUser = get_user_model()

    def get(self, request, *args, **kwargs) -> HttpResponse:
        return render(request, Accounts.Auth.REQUEST_PASSWORD_RESET)

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        email = self.request.POST.get("email")
        user = self.fetch_user(email)
        if user:
            try:
                token_obj = UserToken.objects.generate_token(
                    user=user,
                    token_type=TokenType.PASSWORD_RESET,
                )
                
                resp = self.send_reset_link(user, token_obj.token)
                if not resp:
                    return JsonResponse({
                        "message": "Failed to send password reset email, the mail server took too long to respond.",
                        "error": "Email Delivery Failure",
                        "status": "info",
                        "success": False,
                    }, status=503)
            except Exception as err:
                return JsonResponse({
                        "message": "Something went wrong on our end. We’ve been notified and are looking into it.",
                        "error": "Opps, Something Happened",
                        "status": "warning",
                        "success": False,
                    }, status=500)

        # return render(request, Accounts.Auth.REQUEST_PASSWORD_RESET)

        return JsonResponse({
             "message": f"We’ve sent your password reset link to {email}",
            "title": "Check your Inbox",
            "status": "success",
        }, status=200)

    def fetch_user(self, email) -> Union[AbstractUser, None]:
        try:
            user = self._user_model.objects.get(email=email)
        except self._user_model.DoesNotExist:
            return None
        return user

    def send_reset_link(self, user: AbstractUser, token: str) -> bool:
        """
        Send reset link to user
        """
        if not user.is_verified:
            return False

        login_url = self.request.build_absolute_uri(
            reverse_lazy(
                AuthURLNames.PASSWORD_RESET,
                kwargs={"token": token},
            )
        )

        context = {
            "host": self.request.build_absolute_uri("/"),
            "reset_url": login_url,
        }

        resp = EmailService(user.email).set_subject(
            AccountMails.Subjects.PASSWORD_RESET
        ).use_template(AccountMails.PASSWORD_RESET).with_context(
            **context
        ).send()

        return resp


class NewPasswordView(View):
    """
    Used when a user is not logged in and wants to reset password
    using reset link sent to email address
    """

    http_method_names = ["get", "post"]

    def get(self, request: HttpRequest, *args, **kwargs):
        # context = self.build_context(kwargs.get("token"))
        context = {"token": kwargs.get("token")}
        return render(request, Accounts.Auth.PASSWORD_RESET, context)

    def post(self, request, *args, **kwargs):
        token = kwargs.get("token")
        token_obj = self.fetch_token_obj(token)
        if self.is_token_invalid(token_obj):
            return JsonResponse({
                "status": "error",
                "error": "Expired Token",
                "message": "The password reset link has expired. Please request a new one.",
            }, status=410)
        
        try:
            data = PasswordChangeSchema(**self.request.POST.dict())
            validate_password(data.password1, self.request.user)
            self.change_password(data.password1, token_obj)
            if data.auto_login:
                self.login_user(self.request.user.email, data.password1)
                return JsonResponse({"redirect": True, "url": reverse_lazy(AuthURLNames.ACCOUNT_DASHBOARD)}, status=200)
                # return redirect(reverse_lazy(AuthURLNames.ACCOUNT_DASHBOARD))
        except PydanticError as err:
            from formatters.pydantic_formatter import format_pydantic_errors
            e = format_pydantic_errors(err)
            msg = e[0].get("message").replace("Value error, ", "")
            return JsonResponse({
                "error": "Passwords Do Not Match",
                "message": msg,
                "status": "warning"
                }, status=400)
            
        except DjangoValidationError as err:
            return JsonResponse({
                "error": "Password Policy Violation",
                "message": err.messages[0].replace(':', ','),
                "status": "warning"
                }, status=400)
            
        except Exception as err:
            return JsonResponse({
                "error": "Oops! We hit a snag.",
                "message": "We’re sorry about that! Something went wrong on our end while trying to process your request.",
                "status": "error"
                }, status=500)
            
        # return render(request, Accounts.Auth.PASSWORD_RESET, context)
        return JsonResponse(
            {
                "status": "success",
                "title": "Password Reset Complete",
                "message": "Your password has been updated successfully. You can now log in with your new credentials.",
                "data": {
                    "redirect_url": reverse_lazy(AuthURLNames.LOGIN)
                }
            }, status=200)

    def build_context(self, token: str) -> dict:
        """
        Centralized context building:
        - fetch token
        - determine disabled state
        """
        token_obj = self.fetch_token_obj(token)
        disabled = self.is_token_invalid(token_obj)

        return {
            "token": token,
            "disabled": disabled,
        }

    def fetch_token_obj(self, token: str) -> Optional[UserToken]:
        """Fetch the token object or return None cleanly."""
        try:
            return UserToken.objects.get(
                token=token, token_type=TokenType.PASSWORD_RESET
            )
        except UserToken.DoesNotExist:
            return None

    def is_token_invalid(self, token_obj: Optional[UserToken]) -> bool:
        """Centralized token validation logic."""
        if token_obj is None:
            return True
        if not token_obj.is_valid:
            return True
        if token_obj.has_expired():
            return True
        return False

    @transaction.atomic
    def change_password(
        self, new_password: str, token_obj: UserToken
    ) -> bool:
        """
        Change the user's password and mark token as used.
        Returns True if successful.
        """
        if not token_obj or not token_obj.is_valid:
            return False
        if not new_password:
            raise ValueError("New password can't be None or empty")

        user = token_obj.user
        user.update_password(new_password)

        token_obj.is_valid = False
        token_obj.used_at = timezone.now()
        token_obj.save(update_fields=["used_at", "is_valid"])

        return True

    def login_user(self, email, passwd) -> bool:
        user = authenticate(self.request, username=email, password=passwd)
        if not user:
            return False
        login(self.request, user)
        return True


class ChangePasswordView(LoginRequiredMixin, View):
    """Allows logged-in user to change their password."""

    http_method_names = ["post"]

    def post(self, *args, **kwargs) -> HttpResponse:
        if not self.request.user.can_reset_password():
            return JsonResponse({
                "title": "Security Cooldown Active",
                "message": "To keep your account secure, there is a limit on how often you can reset your password.",
                "status": "info",
            }, status=200)
            
        try:
            data = PasswordChangeSchema(**self.request.POST.dict())
            validate_password(data.password1, self.request.user)
            self.request.user.update_password(data.password1)
            update_session_auth_hash(self.request, self.request.user)
            return JsonResponse({
                "title": "Password Updated",
                "message": "You can now use your new password to log in across all devices.",
                "status": "success"
            }, status=200)
            
        except PydanticError as err:
            from formatters.pydantic_formatter import format_pydantic_errors
            e = format_pydantic_errors(err)
            msg = e[0].get("message").replace("Value error, ", "")
            return JsonResponse({
                "error": "Passwords Do Not Match",
                "message": msg,
                "status": "warning"
                }, status=400)
            
        except DjangoValidationError as err:
            return JsonResponse({
                "error": "Password Policy Violation",
                "message": err.messages[0].replace(':', ','),
                "status": "warning"
                }, status=400)
            
        except Exception as err:
            return JsonResponse({
                "error": "Oops! We hit a snag.",
                "message": "We’re sorry about that! Something went wrong on our end while trying to process your request.",
                "status": "error"
                }, status=500)
