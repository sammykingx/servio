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
from django.db import transaction, IntegrityError
from core.url_names import PaymentURLS
from collaboration.schemas.send_proposal import AppliedRoles, DeliverablesPayload, SendProposal
from registry_utils import get_registered_model
from .exceptions import ProposalError, ProposalPermissionDenied
from .polices import ProposalPolicy
from .status_codes import PolicyFailure
from .validators import ProposalValidator
from typing import Dict, List
import logging


logger = logging.getLogger("app_file")


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

    def send_proposal(self, gig, payload:SendProposal, is_negotiating:bool):
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

            proposal = self.create_proposal_bundle(gig, payload, is_negotiating)
            self.notifications_flow(gig.creator)
            
        except ProposalPermissionDenied as e:
            if e.code == PolicyFailure.SUBSCRIPTION_REQUIRED:
                e.redirect_url = get_error_redirect(e.code, {"gig_id": gig.id})
            raise e
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise
        
        return proposal

    @transaction.atomic
    def create_proposal_bundle(self, gig, payload:SendProposal, is_negotiating: bool):    
        GigModel = get_registered_model("collaboration","Gig")
        gig = (
            GigModel.objects
            .select_for_update(nowait=True)
            .get(id=gig.id)
        )
        proposal = self._create_proposal(gig, payload.proposal_value, payload.sent_at, is_negotiating)
        self._create_proposal_roles(gig, proposal, payload.applied_roles)
        self._create_deliverables(proposal, payload.deliverables)
        
    def _create_proposal(self, gig, proposal_value, sent_at, is_negotiating):
        ProposalModel = get_registered_model("collaboration", "Proposal")
        try:
            proposal = ProposalModel.objects.create(
                gig=gig,
                sender=self.user,
                total_cost=proposal_value,
                sent_at=sent_at,
                is_negotiating=is_negotiating,
            )
            return proposal
        
        except IntegrityError as err:
            if getattr(err.__cause__, "args", None):
                db_error_code = err.__cause__.args[0]
                # MYSQL 1st then sqlite
                if db_error_code == 1062 or "UNIQUE constraint failed" in db_error_code:
                    message=(
                        "It looks like you’ve already shared your "
                        "vision for this project!. Sit tight whilst "
                        "the previous proposal is been reviewed."
                    )
                    raise ProposalPermissionDenied(
                        message,
                        code=PolicyFailure.DUPLICATE_APPLICATION.code,
                        title=PolicyFailure.DUPLICATE_APPLICATION.title,
                    )
            logger.error(
                "Unexpected IntegrityError during proposal creation",
                extra={
                    "user_id": str(self.user.id),
                    "gig_id": str(gig.id),
                })
            raise err
    
    def _create_proposal_roles(self, gig, proposal, applied_roles:List[AppliedRoles]):
        ProposalRoleModel = get_registered_model("collaboration", "ProposalRole")
        GigRoleModel = get_registered_model("collaboration", "GigRole")
        
        role_instances = []
        role_obj = None
        
        for role_payload in applied_roles:
            if gig.has_gig_roles:
                try:
                    role_obj = gig.required_roles.get(
                        role_id=role_payload.niche_id
                    )
                except GigRoleModel.DoesNotExist:
                    raise ProposalPermissionDenied(
                        "It looks like this specific role isn't part of this project's current needs.",
                        code=PolicyFailure.INVALID_ROLE.code,
                        title=PolicyFailure.INVALID_ROLE.title
                    )
                except GigRoleModel.MultipleObjectsReturned:
                    raise ProposalPermissionDenied(
                        "There seems to be a configuration issue with this role.",
                        code=PolicyFailure.INVALID_ROLE.code,
                        title=PolicyFailure.INVALID_ROLE.title
                    )
                role_instances.append(
                    ProposalRoleModel(
                        proposal=proposal,
                        gig_role=role_obj,
                        role_amount=role_payload.role_amount,
                        proposed_amount=role_payload.proposed_amount,
                        payment_plan=role_payload.payment_plan,
                    )
            )
                    
            else:
                ProposalRoleModel.objects.create(
                    proposal=proposal,
                    role_amount=role_payload.role_amount,
                    proposed_amount=role_payload.proposed_amount,
                    payment_plan=role_payload.payment_plan,
                )
                
        if gig.has_gig_roles:
            ProposalRoleModel.objects.bulk_create(role_instances)
        
    def _create_deliverables(self, proposal, deliverables:List[DeliverablesPayload]):
        ProposalDeliverableModel = get_registered_model("collaboration", "ProposalDeliverable")
        deliverable_instances = [
            ProposalDeliverableModel(
                proposal=proposal,
                sender=self.user,
                title=d.title,
                description=d.description,
                duration_unit=d.duration_unit,
                duration_value=d.duration_value,
                due_date=d.due_date,
                order=idx
            )
            for idx, d in enumerate(deliverables)
        ]

        ProposalDeliverableModel.objects.bulk_create(deliverable_instances)
    
    def notifications_flow(self, creator:AbstractUser):
        self._notify_creator_by_mail(creator)
        self._in_app_notifications(creator)
        
    def _notify_creator_by_mail(self, creator:AbstractUser) -> bool:
        if not creator.is_verified:
            print("Not sending any email")
            return False

        return True
    
    def _in_app_notifications(self, creator:AbstractUser) -> None:
        """creates in-app notifications for both providers and creators"""
        return None