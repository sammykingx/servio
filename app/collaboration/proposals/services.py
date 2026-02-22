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
from collaboration.schemas.send_proposal import AppliedRoles, DeliverablesPayload, SendProposal
from registry_utils import get_registered_model
from .exceptions import ProposalError, ProposalPermissionDenied
from .polices import ProposalPolicy
from .status_codes import PolicyFailure
from .validators import ProposalValidator
from typing import Dict, List


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
        try:
            ProposalPolicy.ensure_can_apply(self.user, self.user.profile, gig)
            ProposalValidator.validate(payload, gig)

            proposal = self.create_proposal_bundle(gig, payload)
            self._notify_creator_by_mail(gig.creator)
            # self._create_activity(gig, proposal)
            # self._send_notification(gig, proposal)
            
        except ProposalPermissionDenied as e:
            e.redirect_url = get_error_redirect(e.code, {"gig_id": gig.id})
            raise e
        
        except ProposalError as e:
            raise

        # Future side-effects:
        # self._create_activity(gig, proposal)
        # self._send_notification(gig, proposal)
        
        return proposal

    @transaction.atomic
    def create_proposal_bundle(self, gig, payload:SendProposal):    
        GigModel = get_registered_model("collaboration","Gig")
        gig = (
            GigModel.objects
            .select_for_update(nowait=True)
            .get(id=gig.id)
        )
        proposal = self._create_proposal(gig, payload.proposal_value, payload.sent_at)
        self._create_proposal_roles(proposal, payload.applied_roles)
        self._create_deliverables(proposal, payload.deliverables)
        
    def _create_proposal(self, gig, proposal_value, sent_at):
        ProposalModel = get_registered_model("collaboration", "Proposal")
        proposal = ProposalModel.objects.create(
            gig=gig,
            user=self.user,
            total_cost=proposal_value,
            sent_at=sent_at,
        )
        return proposal
    
    
    def _create_proposal_roles(self, proposal, applied_roles:List[AppliedRoles]):
        ProposalRoleModel = get_registered_model("collaboration", "ProposalRole")
        role_instances = [
            ProposalRoleModel(
                proposal=proposal,
                gig_role_id=role_payload.niche_id,
                role_amount=role_payload.role_amount,
                proposed_amount=role_payload.proposed_amount,
                payment_plan=role_payload.payment_plan,
            )
            for role_payload in applied_roles
        ]

        ProposalRoleModel.objects.bulk_create(role_instances)
        created_roles = list(proposal.roles.all())
        
    def _create_deliverables(self, proposal, deliverables:List[DeliverablesPayload]):
        ProposalDeliverableModel = get_registered_model("collboration", "ProposalDeliverable")
        deliverable_instances = [
            ProposalDeliverableModel(
                proposal=proposal,
                description=d.description,
                duration_unit=d.duration_unit,
                duration_value=d.duration_value,
                due_date=d.due_date,
                order=idx
            )
            for idx, d in enumerate(deliverables)
        ]

        ProposalDeliverableModel.objects.bulk_create(deliverable_instances)
    
    def _notify_creator_by_mail(self, creator:AbstractUser) -> None:
        email = creator.email
        return None
    
    def _in_app_notifications(self, creator:AbstractUser, proovider:AbstractUser) -> None:
        """creates in-app notifications for both providers and creators"""
        return None