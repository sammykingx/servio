from django.views import View
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.views.generic import CreateView
from accounts.forms import UserSignupForm
from services.email_service import EmailService
from template_map.accounts import Accounts
from template_map.emails import AccountMails
from core.url_names import AuthURLNames
from accounts.models.user_tokens import TokenType, UserToken
from allauth.account.views import (
    ConfirmEmailView,
    EmailView, 
    SignupView,
    EmailVerificationSentView,
    EmailConfirmation,
    EmailVerificationStage
)


class CustomSignup(CreateView):
    """
    Custom user registration view.

    Attributes:
        template_name (str): Path to the custom signup template used to
        render the registration interface.
    """
    template_name = Accounts.Auth.SIGNUP
    form_class = UserSignupForm
    success_url = reverse_lazy(AuthURLNames.EMAIL_VERIFICATION_SENT)
    
    def form_valid(self, form:UserSignupForm) -> HttpResponse:
        """
        Process a valid registration form.

        This method is called when the submitted signup form passes
        validation. It saves the new user and performs any additional
        processing required upon successful registration.

        Args:
            form (UserSignupForm): The validated signup form instance.

        Returns:
            HttpResponse: A redirect response to the next page after
            successful registration.
        """
        response = super().form_valid(form)
        email_token, created = UserToken.objects.generate_token(
            user=self.object,
            token_type=TokenType.EMAIL_VERIFICATION,
        )
        self.send_verification_email(token=email_token)
        
        return response
    
    def form_invalid(self, form:UserSignupForm) -> HttpResponse:
        errors = form.errors.as_json()
        print(errors)
        response = super().form_invalid(form)
        return response
    
    def send_verification_email(self, token:str) -> None:
        """
        Send email verification to the newly registered user.
        """
        acct_activation_url = self.request.build_absolute_uri(
            reverse_lazy(
                AuthURLNames.EMAIL_CONFIRMATION,
                kwargs={"token": token}
            )
        )
        
        context={"acct_activation_url": acct_activation_url},
        
        print("ACCOUNT ACTIVATION URL:", acct_activation_url)
        
        
        EmailService(self.object.email) \
            .set_subject(AccountMails.Subjects.EMAIL_VERIFICATION) \
            .use_template(AccountMails.EMAIL_VERIFICATION) \
            .with_context(**context) \
            .send()

        return None

class EmailVerificationView(View):
    """
    
    """
    template_name=Accounts.Auth.SIGNUP_EMAIL_VERIFIED
    success_url = reverse_lazy(AuthURLNames.EMAIL_VERIFIED)