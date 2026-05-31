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
from proposals.models.choices import ProposalRoleStatus, ProposalStatus
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
        pass
        
    
    #----------------- PROPOSAL STATE TRANSISTIONING CHECKS ----------------
    
    @staticmethod
    def _ensure_no_roles_are_finalized(proposal: ProposalEntity) -> None:
        """
        Validates that none of the proposal's individual roles have reached a terminal state.

        A provider is blocked from withdrawing a proposal if the project creator has
        already made a definitive decision (ACCEPTED or REJECTED) on any role within it.

        Args:
            proposal (ProposalEntity): The proposal domain entity with its child 
                roles already cached and available via `.roles`.

        Raises:
            ProposalPermissionDenied: If at least one role in the proposal has an 
                existing status of ACCEPTED or REJECTED.
        """
        finalized_statuses = {ProposalRoleStatus.ACCEPTED, ProposalRoleStatus.REJECTED}
        has_finalized_role = any(role.status in finalized_statuses for role in proposal.roles.all())

        if has_finalized_role:
            failure = PolicyFailure.PROPOSAL_FINALIZED
            raise ProposalPermissionDenied(
                "Cannot withdraw this proposal because one or more roles has reached a terminal state.",
                code=failure.code,
                title=failure.title,
            )
             
    @staticmethod
    def _ensure_provider_only_withdraws(state:ProposalStatus) -> None:
        """
        Restricts the provider's state modification authority exclusively to structural withdrawals.

        Service providers are only allowed to self-mitigate their application by transitioning 
        it to a WITHDRAWN state. Directing the proposal into any other state (like ACCEPTED) 
        requires recipient (Project Creator) authority.

        Args:
            actor (AbstractUser): The user attempting to perform the action.
            proposal (ProposalEntity): The domain representation of the proposal. 
            new_state (ProposalRoleStatus): The target status the actor wants to transition to.

        Raises:
            ProposalPermissionDenied: If the provider attempts any state transition 
                other than ProposalRoleStatus.WITHDRAWN.
        """
        is_withdrawing = state == ProposalStatus.WITHDRAWN

        if not is_withdrawing:
            failure = PolicyFailure.INVALID_ACTION
            raise ProposalPermissionDenied(
                "Only project creators/owners can authorize this action.",
                code=failure.code,
                title=failure.title,
            )
            
    @staticmethod
    def _ensure_is_mutable(proposal: ProposalEntity, payload: ModifyProposalState):
        """
        Validates that the proposal is in a mutable state.

        Raises:
            ProposalPermissionDenied: If the proposal or the specific role has already 
                been finalized (ACCEPTED or WITHDRAWN).
        """
        prop_role = proposal.roles.get(pk=payload.role_id)
        if prop_role.status == ProposalRoleStatus.ACCEPTED or proposal.status == ProposalRoleStatus.WITHDRAWN:
            raise ProposalPermissionDenied(
                "No further action is required because of it's existing decision state.",
                code=PolicyFailure.PROPOSAL_FINALIZED.code,
                title=PolicyFailure.PROPOSAL_FINALIZED.title,
            )
    
    @classmethod
    def check_proposal_action(cls, actor, proposal: ProposalEntity, data: ModifyProposalState):
        # cls.check_financial_status(actor.profile)
        is_provider = proposal.provider == actor
        
        match is_provider:
            case True:
                # service provider validation
                cls._ensure_no_roles_are_finalized(proposal)
                cls._ensure_provider_only_withdraws(data.state)
                
            case False:
                # project creator validation
                cls._ensure_is_mutable(proposal, data)
