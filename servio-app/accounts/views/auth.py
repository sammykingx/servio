from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import View
from django.http import HttpRequest, HttpResponse
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.views import LoginView
from core.url_names import AuthURLNames
from template_map.emails import AccountMails
from services.email_service import EmailService
from accounts.models.user_tokens import UserToken, TokenType
from template_map.accounts import Accounts
from typing import Union


class CustomSignin(LoginView):
    template_name = Accounts.Auth.SIGNIN
    redirect_authenticated_user = True
    success_url = reverse_lazy(AuthURLNames.ACCOUNT_DASHBOARD)

    def form_invalid(self, form) -> HttpResponse:
        errors = form.errors.as_json()
        print(errors)
        response = super().form_invalid(form)
        return response


class SigninLinkView(View):
    http_method_names = ["get", "post"]
    _user_model: AbstractUser = get_user_model()

    def get(self, request, **kwargs) -> HttpResponse:
        return render(
            request,
            Accounts.Auth.SIGNIN_ACCESS_CODE,
        )

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        email = self.request.POST.get("email")
        user = self.fetch_user(email)
        if user is None:
            return render(request, Accounts.Auth.SIGNIN_ACCESS_CODE_SENT)

        token = self.fetch_token(user)
        self.send_signin_link(user, token)

        return render(
            request,
            Accounts.Auth.SIGNIN_ACCESS_CODE_SENT,
        )

    def fetch_token(self, user: AbstractUser):
        return UserToken.objects.generate_token(
            user=user,
            token_type=TokenType.MAGIC_LINK,
        ).token

    def fetch_user(self, email) -> Union[AbstractUser, None]:
        try:
            user = self._user_model.objects.get(email=email)
        except self._user_model.DoesNotExist:
            return None
        return user

    def send_signin_link(self, user: AbstractUser, token: str) -> bool:
        """
        Send magic link to user
        """
        login_url = self.request.build_absolute_uri(
            reverse_lazy(
                AuthURLNames.VERIFY_LOGIN_LINK,
                kwargs={"token": token},
            )
        )

        context = {
            "host": self.request.build_absolute_uri("/"),
            "login_url": login_url,
        }

        EmailService(user.email).set_subject(
            AccountMails.Subjects.LOGIN_LINK
        ).use_template(AccountMails.MAGIC_LINK).with_context(
            **context
        ).send()

        return True


class VerifySigninLinkView(View):
    http_method_names = ["get"]

    def get(self, request, **kwargs) -> HttpResponse:
        token = kwargs.get("token")
        user = authenticate(request, token=token)
        if user is None:
            return render(
                request, Accounts.Auth.SIGNIN_ACCESS_CODE_FAILED
            )
        login(request, user)
        return redirect(reverse_lazy(AuthURLNames.ACCOUNT_DASHBOARD))


__all__ = [CustomSignin, SigninLinkView, VerifySigninLinkView]
