from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import View
from django.contrib.auth import get_user_model
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.views import LoginView
from core.url_names import AuthURLNames
from template_map.emails import AccountMails
from services.email_service import EmailService
from accounts.models.user_tokens import UserToken, TokenType
from template_map.accounts import Accounts


class CustomSignin(LoginView):
    template_name = Accounts.Auth.SIGNIN
    
    def form_invalid(self, form) -> HttpResponse:
        errors = form.errors.as_json()
        print(errors)
        response = super().form_invalid(form)
        return response

class SigninLinkView(View):
    http_method_names = ["get", "post"]
    _user_model = get_user_model()
    
    def get(self, request, **kwargs) -> HttpResponse:
        return render(
            request,
            Accounts.Auth.SIGNIN_ACCESS_CODE,
        )
    
    def post(self, request:HttpRequest, *args, **kwargs) -> HttpResponse:
        email = self.request.get("email")
        user = self.fetch_user(email)
        if not user:
            render(request, Accounts.Auth.SIGNUP_VERV_EMAIL_SENT)
        
        result = self.fetch_token(user)
        self.send_signin_link(result.token)
        
        return render(
            request,
            Accounts.Auth.SIGNIN_ACCESS_CODE_SENT,
        )
    
    def fetch_token(self, user):
        return UserToken.objects.generate_token(
            user=user,
            token_type=TokenType.MAGIC_LINK,
        )
        
    def fetch_user(self, email):
        user = self._user_model.objects.filter(email=email)
        if user and user.is_verified:
            return None
        return user
           
    def send_signin_link(self, user, token:str) -> None:
        """
        Send magic link to user
        """
        login_url = self.request.build_absolute_uri(
            reverse_lazy(
                AuthURLNames.VERIFY_LOGIN_LINK,
                kwargs={"token": token}
            )
        )
        
        context = {
            "host": self.request.build_absolute_uri("/"),
            "login_url": login_url,
        }
        
        EmailService(user.email) \
            .set_subject(AccountMails.Subjects.LOGIN_LINK) \
            .use_template(AccountMails.MAGIC_LINK) \
            .with_context(**context) \
            .send()

        return None
            

class VerifySigninLinkView(View):
    http_method_names = ["get"]
 


__all__ = [CustomSignin, SigninLinkView, VerifySigninLinkView]