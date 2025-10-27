"""
Accounts Template Map
---------------------
Centralized registry for all HTML template file paths related to the **Accounts** app.

This module follows a class-based, nested structure for organizing templates in a
clean, DRY, and maintainable way.
"""

from . import TemplateRegistryBase

_BASE_FOLDER = TemplateRegistryBase("accounts")

class Accounts:
    """Namespace container for all 'accounts' app templates."""

    class Auth:
        """
        Authentication-related templates.

        Folder: templates/accounts/authentication/
        Contains HTML templates for user login, registration, logout, and password reset.
        """

        __SUB_FOLDER = _BASE_FOLDER.subfolder("authentication")

        SIGNIN = f"{__SUB_FOLDER}/signin.html"
        SIGNIN_OPTIONS = f"{__SUB_FOLDER}/signin-options.html"
        SIGNIN_ACCESS_CODE = f"{__SUB_FOLDER}/request-access-code.html"
        
        SIGNUP = f"{__SUB_FOLDER}/signup.html"
        SIGNUP_VERV_EMAIL_SENT = f"{__SUB_FOLDER}/email-verification-sent.html"
        SIGNUP_EMAIL_VERIFIED = f"{__SUB_FOLDER}/email-verified.html"
        
        PASSWORD_RESET = f"{__SUB_FOLDER}/reset-password.html"

    class Dashboards:
        """
        User dashboard templates.

        Folder: templates/accounts/dashboards/
        Contains role-specific dashboards for admin, users, and service provider accounts.
        """

        __SUB_FOLDER = _BASE_FOLDER.subfolder("dashboards")

        ADMIN = f"{__SUB_FOLDER}/admin.html"
        USERS = f"{__SUB_FOLDER}/users.html"
        SERVICE_PROVIDER = f"{__SUB_FOLDER}/service-provider.html"
        
        
        
__all__ = [Accounts]

