from template_map.accounts import Accounts
from allauth.account.views import (
    LoginView, 
    SignupView, 
    PasswordResetView, 
    PasswordChangeView,
    PasswordResetDoneView,
)


class CustomSignin(LoginView):
    template_name = Accounts.Auth.SIGNIN
    

class CustomSignup(SignupView):
    template_name = Accounts.Auth.SIGNUP
    

class CustomPasswordReset(PasswordResetView):
    template_name = Accounts.Auth.PASSWORD_RESET
    
    
__all__ = [CustomSignin, CustomSignup, CustomPasswordReset]