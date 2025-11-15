from django.views import View
from django.shortcuts import render
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.views.generic import CreateView
from accounts.forms import UserSignupForm
from services.email_service import EmailService
from template_map.accounts import Accounts
from template_map.emails import AccountMails
from core.url_names import AuthURLNames
from accounts.models.user_tokens import TokenType, UserToken


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
        self.send_verification_email(email_token)
        
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
        
        context = {
            "host": self.request.build_absolute_uri("/"),
            "acct_activation_url": acct_activation_url,
        }
        
        EmailService(self.object.email) \
            .set_subject(AccountMails.Subjects.EMAIL_VERIFICATION) \
            .use_template(AccountMails.EMAIL_VERIFICATION) \
            .with_context(**context) \
            .send()

        return None

class EmailVerificationView(View):
    """
    
    """
    http_method_names = ["get"]
    
    def get(self, request, **kwargs) -> HttpResponse:
        token = kwargs.get("token")
        user_token = self.fetch_token_obj(token=token)
        
        return render(
            request,
            Accounts.Auth.SIGNUP_EMAIL_VERIFIED,
        )
        
    def fetch_token_obj(self, token:str):
        try:
            user_token = UserToken.objects.get(token=token)
            
        except UserToken.DoesNotExist:
            # attach the message
            return None

        return _user
    
    def activate_account(self, token: str) -> None:
        """
            updates user is_verified status to true directly
            on the database.
            
            Note: This doesn't updates the previous call to
            user model, so previous call will still have it's
            is_verified property false if the user wasn't verified.
        """

        if not user.is_verified:
            user.__class__.objects.filter(pk=user.pk).update(is_verified=True)
            
        return None
