from template_map.accounts import Accounts
from django.urls import reverse_lazy
from core.url_names import AuthURLNames
from allauth.account.views import (
    LoginView,
    RequestLoginCodeView,
    ConfirmLoginCodeView,
    LogoutView
)


class CustomSignin(LoginView):
    template_name = Accounts.Auth.SIGNIN

    
class GetLoginAccessCode(RequestLoginCodeView):
    template_name = Accounts.Auth.SIGNIN_ACCESS_CODE
 

class VerifyLoginAccessCode(ConfirmLoginCodeView):
    pass


__all__ = [CustomSignin, GetLoginAccessCode, VerifyLoginAccessCode]