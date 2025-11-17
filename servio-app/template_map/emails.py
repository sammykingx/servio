"""
Accounts Template Map
---------------------
Centralized registry for all HTML email template file paths related to the **Accounts** app.

This module follows a class-based, nested structure for organizing templates in a
clean, DRY, and maintainable way.
"""

from . import TemplateRegistryBase

_BASE_FOLDER = TemplateRegistryBase("emails")

class AccountMails:
    """Namespace container for all 'accounts' email templates."""
    
    # WELCOME_EMAIL = f"{_BASE_FOLDER}/welcome-email.html"
    EMAIL_VERIFICATION = _BASE_FOLDER.base_folder_files("email-verification.html")
    MAGIC_LINK = _BASE_FOLDER.base_folder_files("magic-link.html")
    PASSWORD_RESET = f"{_BASE_FOLDER}/password-reset.html"
    
    class Subjects:
        """Namespace container for email subject lines."""
        
        WELCOME_EMAIL = "Welcome to Servio!"
        EMAIL_VERIFICATION = "Please Confirm Your Email Address - Divgm"
        PASSWORD_RESET = "Action Required: Reset Your Password - Divgm"
        LOGIN_LINK = "Your One-Tap Login Is Ready - Divgm"
    
        
__all__ = [AccountMails]


