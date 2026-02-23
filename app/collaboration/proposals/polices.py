"""
PROPOSAL POLICIES
=================

PURPOSE:
Enforces Business Eligibility and Authorization.
Answers: "Is this specific User/Action allowed in the current context?"

SCOPE:
- Contextual Authorization (e.g., Ownership, Roles, Subscriptions, etc).
- State-based Restrictions (e.g., Is the Gig still 'Published'?).
- Eligibility Logic (e.g., Has the Provider paid their one-time fee?).
- Deterministic Logic: Should be side-effect free.

NON-GOALS:
- Data Integrity (Use Validators for payload/format checks).
- Persistence (No DB writes; logic should be based on passed objects).
- Side Effects (No emails, notifications, or state mutations).
"""

from django.utils import timezone
from collaboration.models.choices import GigStatus, RoleStatus
from .exceptions import ProposalPermissionDenied
from .status_codes import PolicyFailure
from registry_utils import get_registered_model

GigsModel = get_registered_model("collaboration", "Gig")
GigRole = get_registered_model("collaboration", "GigRole")

class ProposalPolicy:
    """
    Stateless decision logic for proposal-related actions.
    """

    @staticmethod
    def check_gig_eligibility(gig, user):
        """Validates if the Gig is in a state to accept proposals."""    
        if gig.creator == user:
            raise ProposalPermissionDenied(
                "You cannot apply to your own projects.",
                code=PolicyFailure.CANNOT_APPLY_TO_OWN_GIG.code,
                title=PolicyFailure.CANNOT_APPLY_TO_OWN_GIG.title
            )
            
        if gig.status == GigStatus.IN_PROGRESS:
            raise ProposalPermissionDenied(
                "Applications for this gig are closed as the project has already commenced.",
                code=PolicyFailure.GIG_ALREADY_STARTED.code,
                title=PolicyFailure.GIG_ALREADY_STARTED.title
            )

        if gig.status != GigStatus.PUBLISHED:
            raise ProposalPermissionDenied(
                "This project is no longer accepting applications.",
                code=PolicyFailure.GIG_NOT_PUBLISHED.code,
                title=PolicyFailure.GIG_NOT_PUBLISHED.title
            )
            
        if gig.start_date and timezone.now().date() > gig.start_date:
            raise ProposalPermissionDenied(
                "The application window for this project has closed as the start date has passed.",
                code=PolicyFailure.GIG_START_DATE_PASSED.code,
                title=PolicyFailure.GIG_START_DATE_PASSED.title
            )

    @staticmethod
    def check_user_eligibility(profile, gig):
        """Validates if the user is qualified for this specific gig."""
        
        if not profile.user.is_verified:
            raise ProposalPermissionDenied(
                "Verify your email to ensure your negotiations and contracts remain legally sound.",
                code=PolicyFailure.EMAIL_NOT_VERIFIED.code,
                title=PolicyFailure.EMAIL_NOT_VERIFIED.title,
            )
            
        if gig.has_gig_roles:
            is_qualified = GigRole.objects.filter(
                status=RoleStatus.OPEN,
                niche_id=profile.industry_id,
                role_id__in=profile.get_user_niches,
                gig=gig
            ).exists()

            if not is_qualified:
                raise ProposalPermissionDenied(
                    "Your profile does not match the project role's requirements.",
                    code=PolicyFailure.NOT_QUALIFIED_FOR_ROLES.code,
                    title=PolicyFailure.NOT_QUALIFIED_FOR_ROLES.title
                )

    @staticmethod
    def check_financial_status(profile):
        """Checks if the user has paid necessary fees."""
        if not profile.has_paid_onetime_fee:
            raise ProposalPermissionDenied(
                "Please pay the one-time registration fee to apply.",
                code=PolicyFailure.SUBSCRIPTION_REQUIRED.code,
                title=PolicyFailure.SUBSCRIPTION_REQUIRED.title,
            )

    @classmethod
    def ensure_can_apply(cls, user, profile, gig) -> None:
        """
        Orchestrator: Runs all checks. 
        If any fail, they raise a ProposalPermissionDenied with a specific message.
        """
        cls.check_gig_eligibility(gig, user)
        cls.check_user_eligibility(profile, gig)
        cls.check_financial_status(profile)
        
