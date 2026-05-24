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

from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from core.model_registry import registry
from collaboration.models.choices import ProjectStatus, ProjectRoleStatus
from proposals.models.choices import ProposalRoleStatus
from proposals.application.dto.modify_proposal_state import ModifyProposalState
from ..exceptions import ProposalPermissionDenied
from ..status_codes import PolicyFailure
from ...domain.entities import ProjectEntity, ProposalEntity
from typing import Literal


GigsModel = registry.Gig
GigRole = registry.GigRole
Proposal = registry.Proposal

class ProposalPolicy:
    """
    Stateless decision logic for proposal-related actions.
    """
    
    @staticmethod
    def check_project_state(project: ProjectEntity, actor: AbstractUser):
        """Validates if the project is in a state to accept proposals."""
        if project.creator == actor:
            raise ProposalPermissionDenied(
                "You cannot apply to your own projects.",
                code=PolicyFailure.CANNOT_APPLY_TO_OWN_PROJECT.code,
                title=PolicyFailure.CANNOT_APPLY_TO_OWN_PROJECT.title,
            )

        if project.status == ProjectStatus.IN_PROGRESS:
            raise ProposalPermissionDenied(
                "Applications for this project are closed as the project has already commenced.",
                code=PolicyFailure.GIG_ALREADY_STARTED.code,
                title=PolicyFailure.GIG_ALREADY_STARTED.title,
            )

        if project.status != ProjectStatus.PUBLISHED:
            raise ProposalPermissionDenied(
                "This project is no longer accepting applications.",
                code=PolicyFailure.PROJECT_NOT_PUBLISHED.code,
                title=PolicyFailure.PROJECT_NOT_PUBLISHED.title,
            )

        if project.start_date and timezone.now().date() > project.start_date:
            raise ProposalPermissionDenied(
                "The application window for this project has closed as the start date has passed.",
                code=PolicyFailure.PROJECT_START_DATE_PASSED.code,
                title=PolicyFailure.PROJECT_START_DATE_PASSED.title,
            )

    @staticmethod
    def check_user_eligibility(profile, project: ProjectEntity):
        """Validates if the user is qualified for this specific project."""

        if not profile.user.is_verified:
            raise ProposalPermissionDenied(
                "Verify your email to ensure your negotiations and contracts remain legally sound.",
                code=PolicyFailure.EMAIL_NOT_VERIFIED.code,
                title=PolicyFailure.EMAIL_NOT_VERIFIED.title,
            )

        if project.has_gig_roles:
            is_qualified = GigRole.objects.filter(
                status=ProjectRoleStatus.OPEN,
                niche_id=profile.industry_id,
                role_id__in=profile.get_user_niches,
                gig=project.id,
            ).exists()

            if not is_qualified:
                raise ProposalPermissionDenied(
                    "Your profile does not match the project role's requirements.",
                    code=PolicyFailure.NOT_QUALIFIED_FOR_ROLES.code,
                    title=PolicyFailure.NOT_QUALIFIED_FOR_ROLES.title,
                )

    @staticmethod
    def check_financial_status(profile):
        """Checks if the user has paid necessary fees."""
        if not profile.has_paid_onetime_fee:
            raise ProposalPermissionDenied(
                "Please pay the one-time sign-on fee to proceed",
                code=PolicyFailure.SUBSCRIPTION_REQUIRED.code,
                title=PolicyFailure.SUBSCRIPTION_REQUIRED.title,
            )
            
    @classmethod
    def ensure_can_apply(cls, actor: AbstractUser, project: ProjectEntity) -> None:
        """
        Orchestrator: Runs all checks.
        If any fail, they raise a ProposalPermissionDenied with a specific message.
        """
        cls.check_user_eligibility(actor.profile, project)
        cls.check_project_state(project, actor)
        # cls.check_financial_status(actor.profile)
        
    
    @staticmethod
    def validate_state_transition(actor: AbstractUser, proposal: ProposalEntity, new_state: ProposalRoleStatus):
        """
        Ensures a provider can only move a proposal to a WITHDRAWN state.
        Any other transition requires recipient (Project Creator) authority.
        """
        is_provider = proposal.provider == actor
        is_withdrawing = new_state == ProposalRoleStatus.WITHDRAWN

        if is_provider and not is_withdrawing:
            failure = PolicyFailure.INVALID_ACTION_FOR_PROVIDER
            raise ProposalPermissionDenied(
                "Only the project creators can authorize this action.",
                code=failure.code,
                title=failure.title,
            )
    
    
    @classmethod
    def should_modify_state(cls, actor, proposal: ProposalEntity, payload:ModifyProposalState):
        cls.validate_state_transition(actor, proposal, payload.state)
        # cls.check_financial_status(actor.profile)
        # checkif previously assigned for gigs with roles
        # if previously assigned check if reassign is in payload
