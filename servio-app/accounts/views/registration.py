from template_map.accounts import Accounts
from allauth.account.views import (
    ConfirmEmailView,
    EmailView, 
    SignupView, 
    email_verification_sent,
)


class CustomSignup(SignupView):
    """
    Custom user registration view.

    Attributes:
        template_name (str): Path to the custom signup template used to
        render the registration interface.
    """
    template_name = Accounts.Auth.SIGNUP
    
    
class EmailConfirmation(ConfirmEmailView):
    """
    Email confirmation handler.

    This view processes the verification link sent to a user's email
    after signup. It verifies the provided key and activates the
    associated user account if key is valid.
    """
    pass


class EmailConfirmationSent:
    """
    Notification view for verification email dispatch.

    This renders the page notifying the user the a verification email
    has been successfully sent to the registered email address.
    """
    pass


class ManageAccountEmail(EmailView):
    """
    Users manage the email addresses tied to their account.
    
    Here, users can add (and verify) email addresses, remove email,
    choose a new primary email address.
    """
    pass