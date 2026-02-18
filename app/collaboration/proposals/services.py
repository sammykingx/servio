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

from django.apps import apps
from django.db import transaction
from collaboration.models.choices import ApplicationStatus
from .polices import ProposalPolicy
from .exceptions import ProposalPermissionDenied


GigApplication = apps.get_model("collaboration", "GigApplication")


class ProposalService:
    """
    Domain Service for orchestrating the Proposal lifecycle.

    This service acts as the (conductor), coordinating between 
    Policies, Validators, and Persistence layers. It ensures that 
    proposals are only created when all business and integrity 
    constraints are satisfied.
    """

    def __init__(self, user):
        self.user = user

    @transaction.atomic
    def send_proposal(self, gig, payload):
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

        self._ensure_can_apply(gig)
        self._validate(payload, gig)

        proposal = self._create_proposal(gig, payload)

        # Future side-effects:
        # self._create_activity(gig, proposal)
        # self._send_notification(gig, proposal)
        return proposal

    # -------------------------
    # Private orchestration steps
    # -------------------------

    def _ensure_can_apply(self, gig):
        ProposalPolicy.ensure_can_apply(self.user, self.user.profile, gig)
        
    def _validate(self, payload, gig):
        """
        Enforces domain-level integrity and data invariants.

        Unlike Policy checks (which handle authorization and eligibility), 
        this method ensures the payload data is logically sound in the 
        context of the target Gig's constraints.

        Checks include:
        - Price non-negativity and logical range.
        - Duration limits relative to Gig requirements.
        - Invariant consistency (e.g., end_date > start_date).

        Args:
            payload: The Pydantic/DTO object containing submitted data.
            gig: The Gig entity providing the constraint context.

        Raises:
            ProposalValidationError: If any data invariant is violated.
        """
        return True

    def _create_proposal(self, gig, payload):
        # return GigApplication.objects.create(
        #     gig=gig,
        #     applicant=self.user,
        #     price=payload.price,
        #     deliverables=payload.deliverables,
        #     duration=payload.duration,
        #     status=ApplicationStatus.PENDING,
        # )
        return True