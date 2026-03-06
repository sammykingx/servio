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
    EMAIL_VERIFICATION = _BASE_FOLDER.base_folder_files(
        "email-verification.html"
    )
    MAGIC_LINK = _BASE_FOLDER.base_folder_files("magic-link.html")
    PASSWORD_RESET = _BASE_FOLDER.base_folder_files("password-reset.html")

    class Subjects:
        """Namespace container for email subject lines."""

        WELCOME_EMAIL = "Welcome to Servio!"
        EMAIL_VERIFICATION = "Please Confirm Your Email Address - Divgm"
        PASSWORD_RESET = "Action Required: Reset Your Password - Divgm"
        LOGIN_LINK = "Your One-Tap Login Is Ready - Divgm"
        
        
class ProposalMails:
    """Namespace container for all 'proposals' mail templates."""
    
    __SUB_FOLDER = _BASE_FOLDER.subfolder("proposals")
    
    PROPOSAL_RECEIVED = f"{__SUB_FOLDER}/proposal-received.html"
    PROPOSAL_ACCEPTED = f"{__SUB_FOLDER}/proposal-accepted.html"
    PROPOSAL_REJECTED = f"{__SUB_FOLDER}/proposal-rejected.html"
    PROPOSAL_COUNTERED = f"{__SUB_FOLDER}/proposal-countered.html"
    
    class Subjects:
        PROPOSAL_RECEIVED = "New Proposal Received for Your project - Divgm"
        PROPOSAL_ACCEPTED = "Congratulations! Your Proposal Was Accepted - Divgm"
        PROPOSAL_REJECTED = "Update on Your Proposal - Divgm"
        PROPOSAL_COUNTERED = "Your Proposal Has Been Countered - Divgm"


__all__ = [AccountMails, ProposalMails]
