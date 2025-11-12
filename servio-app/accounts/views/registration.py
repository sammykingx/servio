from template_map.accounts import Accounts
from django.views.generic import CreateView
from accounts.forms import UserSignupForm
from django.urls import reverse_lazy
from core.url_names import AuthURLNames
from allauth.account.adapter import get_adapter
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
        print(self.object)
        response = super().form_valid(form)
        self.send_verification_email()
        # send user activation email in bg process
        
        return response
    
    def form_invalid(self, form):
        errors = form.errors.as_json()
        print(errors)
        response = super().form_invalid(form)
        return response
    
    def send_verification_email(self):
        """
        Send email verification to the newly registered user.
        """
        # email token
        key = get_adapter().generate_emailconfirmation_key(self.object)
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