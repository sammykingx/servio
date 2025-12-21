"""
Accounts Template Map
---------------------
Centralized registry for all HTML template file paths related to the **Accounts** app.

This module follows a class-based, nested structure for organizing templates in a
clean, DRY, and maintainable way.
"""

from . import TemplateRegistryBase

_BASE_FOLDER = TemplateRegistryBase("account")


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
        SIGNIN_ACCESS_CODE_SENT = (
            f"{__SUB_FOLDER}/request-access-code-sent.html"
        )
        SIGNIN_ACCESS_CODE_FAILED = (
            f"{__SUB_FOLDER}/request-access-code-failed.html"
        )

        SIGNUP = f"{__SUB_FOLDER}/signup.html"
        SIGNUP_VERV_EMAIL_SENT = (
            f"{__SUB_FOLDER}/email-verification-sent.html"
        )
        SIGNUP_EMAIL_VERIFIED = f"{__SUB_FOLDER}/email-verified.html"

        REQUEST_PASSWORD_RESET = (
            f"{__SUB_FOLDER}/request-password-reset.html"
        )
        PASSWORD_RESET = f"{__SUB_FOLDER}/password-reset.html"

    class Dashboards:
        """
        User dashboard templates.

        Folder: templates/accounts/dashboards/
        Contains role-specific dashboards for admin, users, and service provider accounts.
        """

        __SUB_FOLDER = _BASE_FOLDER.subfolder("dashboards")

        ADMIN = f"{__SUB_FOLDER}/admin.html"
        MEMBERS = f"{__SUB_FOLDER}/members.html"
        PROVIDERS = f"{__SUB_FOLDER}/providers.html"
        STAFFS = f"{__SUB_FOLDER}/staff.html"
        
    class Business:
        __SUB_FOLDER = _BASE_FOLDER.subfolder("business")
        
        BUSINESS_INFO = f"{__SUB_FOLDER}/business-info.html"
        BUSINESS_PROFILE = f"{__SUB_FOLDER}/business-page.html"
        BUSINESS_SERVICES = F"{__SUB_FOLDER}/business-services.html"
        

    ACCOUNT_PROFILE = _BASE_FOLDER.base_folder_files("profile.html")
    ACCOUNT_SETTINGS = _BASE_FOLDER.base_folder_files(
        "account-settings.html"
    )


__all__ = [Accounts]
