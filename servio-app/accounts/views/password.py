from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordChangeView,
    PasswordChangeDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from django.urls import reverse_lazy
from core.url_names import AuthURLNames
from template_map.accounts import Accounts
from template_map.emails import AccountMails


class PasswordResetEmailView(PasswordResetView):
    """
    Allows a user to reset their password by generating a
    one-time use link that can be used to reset the password,
    and sending that link to the user’s registered email address.
    """
    template_name = Accounts.Auth.PASSWORD_RESET
    email_template_name = html_email_template_name = AccountMails.PASSWORD_RESET
    subject_template_name = AccountMails.Subjects.PASSWORD_RESET
    success_url = reverse_lazy(AuthURLNames.PASSWORD_RESET_DONE)


class PasswordResetEmailDOneView(PasswordResetDoneView):
    """
    The page shown after a user has been emailed a link to
    reset their password.
    """
    
    pass

class ChangePasswordView(PasswordChangeView):
    """Allows a user to change their password."""
    
    # Used when the logged-in user wants to change their own password
    # Key characteristics:
    #   - User must be authenticated
    #   - User must know their current password
    #   - Typical use: “Change Password” inside user settings
    #   - Does not involve email or tokens
    
    # User is logged in
    # They go to /accounts/password/change/
    # They enter:
    #   current password
    #   new password
    #   confirm password
    # Password changes immediately
    # User stays logged in (unless configured otherwise)
    
    pass

class ChangePasswordCompleteView(PasswordChangeDoneView):
    """The page shown after a user has changed their password."""
    
    pass

class NewPasswordView(PasswordResetConfirmView):
    """
        Used when a user is not logged in and wants to reset password
        via email
    """
    
class NewPasswordSetView(PasswordResetCompleteView):
    """
        Presents a view which informs the user that the password has
        been successfully changed.
    """