from template_map.accounts import Accounts
from allauth.account.views import (
    ConfirmEmailView,
    EmailView, 
    SignupView,
    EmailVerificationSentView,
    EmailConfirmation,
    EmailVerificationStage
)


class CustomSignup(SignupView):
    """
    Custom user registration view.

    Attributes:
        template_name (str): Path to the custom signup template used to
        render the registration interface.
    """
    template_name = Accounts.Auth.SIGNUP
    
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
            form (SignupForm): The validated signup form instance.

        Returns:
            HttpResponse: A redirect response to the next page after
            successful registration.
        """
        response = super().form_valid(form)
        
        return response
    
    def form_invalid(self, form):
        errors = form.errors.as_json()
        response = super().form_invalid(form)
        return response
    
    
class EmailConfirmation(ConfirmEmailView):
    """
    Email confirmation handler.

    This view processes the verification link sent to a user's email
    after signup. It verifies the provided key and activates the
    associated user account if key is valid.
    """
    template_name = Accounts.Auth.SIGNUP_EMAIL_VERIFIED


class EmailConfirmationSent(EmailVerificationSentView):
    """
    Notification view for verification email dispatch.

    This renders the page notifying the user that a verification email
    has been sent successfully to the registered email address.
    """
    template_name = Accounts.Auth.SIGNUP_VERV_EMAIL_SENT


class ManageAccountEmail(EmailView):
    """
    Users manage the email addresses tied to their account.
    
    Here, users can add (and verify) email addresses, remove email,
    choose a new primary email address.
    """
    pass