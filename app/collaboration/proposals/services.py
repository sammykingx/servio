"""
PROPOSAL SERVICES MODULE
========================

Purpose
-------
This module contains application-level use cases for proposal workflows.
Services orchestrate the sequence of actions required to execute a feature.

Responsibilities
----------------
- Coordinate policies and validators
- Enforce business rules through domain modules
- Create/update proposal records
- Trigger side effects (activity logs, notifications, etc.)
- Manage transactional workflow

This module MUST NOT:
---------------------
- Contain HTTP logic (no request/response handling)
- Implement permission rules directly (use policies)
- Implement business validation rules directly (use validators)

Services orchestrate. Domain modules decide and validate.
"""

from django.contrib.auth.models import AbstractUser
from django.urls import reverse_lazy
from django.db import transaction
from core.url_names import PaymentURLS
from collaboration.schemas.send_proposal import SendProposal
from registry_utils import get_registered_model
from .exceptions import ProposalPermissionDenied
from .polices import ProposalPolicy
from .status_codes import PolicyFailure
from .validators import ProposalValidator


ProposalModel = get_registered_model("collaboration", "Proposal")

def get_error_redirect(code: str, context: dict = None) -> str:
    """
    Maps failure codes to their respective redirect paths.
    Using a context dict allows for dynamic URL construction (IDs, etc).
    """
    context = context or {}
    
    mapping = {
        PolicyFailure.SUBSCRIPTION_REQUIRED.code: reverse_lazy(PaymentURLS.PAY_SUBSCRIPTION),
        PolicyFailure.PAYMENT_PENDING.code: "#",
        # Example of a dynamic URL using context
        # ValidationFailure.INVALID_ROLE.code: f"/gigs/{context.get('gig_id')}/roles/",
    }
    
    return mapping.get(code)


class ProposalService:
    """
    Domain Service for orchestrating the Proposal lifecycle.

    This service acts as the (conductor), coordinating between 
    Policies, Validators, and Persistence layers. It ensures that 
    proposals are only created when all business and integrity 
    constraints are satisfied.
    """

    def __init__(self, user:AbstractUser):
        self.user = user

    @transaction.atomic
    def send_proposal(self, gig, payload:SendProposal):
        """
        Executes the end-to-end proposal submission process.

        Workflow:
        1. Eligibility: Check Policy rules (User/Gig context).
        2. Integrity: Validate Payload invariants (Data logic).
        3. Persistence: Create the GigApplication record.
        4. Side Effects: Trigger notifications/activity logs (Future).

        Args:
            gig (Gig): The target Aggregate being applied to.
            payload (ProposalDTO/Object): The validated pydantic data for the proposal.

        Returns:
            GigApplication: The newly created proposal instance.

        Raises:
            ProposalPermissionDenied: If policy checks fail.
            ProposalValidationError: If data integrity checks fail.
        """
        # prevent double cliks
        try:
            ProposalPolicy.ensure_can_apply(self.user, self.user.profile, gig)
            ProposalValidator.validate(payload, gig)

            proposal = self._create_proposal(gig, payload)
            self._notify_creator_by_mail(gig.creator)
            # self._create_activity(gig, proposal)
            # self._send_notification(gig, proposal)
            
        except ProposalPermissionDenied as e:
            e.redirect_url = get_error_redirect(e.code, {"gig_id": gig.id})
            raise e

        # Future side-effects:
        # self._create_activity(gig, proposal)
        # self._send_notification(gig, proposal)
        return proposal

    def _create_proposal(self, gig, payload):
        
        # ERRORS TO PREVENT
        # - raise conditions
        # - no duplicate application for same gig for the current user
        
        # return GigApplication.objects.create(
        #     gig=gig,
        #     applicant=self.user,
        #     price=payload.price,
        #     deliverables=payload.deliverables,
        #     duration=payload.duration,
        #     status=ApplicationStatus.PENDING,
        # )
        return True
    
    def _notify_creator_by_mail(self, creator:AbstractUser) -> None:
        email = creator.email
        return None
    
    def _in_app_notifications(self, creator:AbstractUser, proovider:AbstractUser) -> None:
        """creates in-app notifications for both providers and creators"""
        return None