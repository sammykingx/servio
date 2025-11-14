from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.template.loader import render_to_string
from accounts.forms import UserSignupForm
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
    
    # def dispatch(self, request, *args, **kwargs):
    #     print(">>> DISPATCH:", request.method)
    #     return super().dispatch(request, *args, **kwargs)

    
    def form_valid(self, form):
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
        # send mssgs to FE
        # send user activation email in bg process
        
        return response
    
    def form_invalid(self, form):
        errors = form.errors.as_json()
        print(errors)
        response = super().form_invalid(form)
        return response
    
    def send_verification_email(self, token):
        """
        Send email verification to the newly registered user.
        """
        acct_activation_url = self.request.build_absolute_uri(
            reverse_lazy(
                AuthURLNames.EMAIL_CONFIRMATION,
                kwargs={"token": token}
            )
        )
        
        print("ACCOUNT ACTIVATION URL:", acct_activation_url)
        
        msg = render_to_string(
            template_name=AccountMails.EMAIL_VERIFICATION,
            context={"acct_activation_url": acct_activation_url},
        )
        # email template
        # template context: acct_activation_url
        # send email
        pass

class ManageAccountEmail(EmailView):
    """
    Users manage the email addresses tied to their account.
    
    Here, users can add (and verify) email addresses, remove email,
    choose a new primary email address.
    """
    pass