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
from django.db import transaction, IntegrityError, OperationalError
from core.url_names import PaymentURLS
from collaboration.models.choices import ProposalRoleStatus
from collaboration.schemas.send_proposal import (
    AppliedRoles,
    DeliverablesPayload,
    SendProposal,
)
from collaboration.schemas.modify_proposal_state import ModifyProposalState
from constants import SERVICE_FEE, DECIMAL_PLACE
from registry_utils import get_registered_model
from services.email_service import EmailService
from template_map.emails import ProposalMails
from .exceptions import ProposalError, ProposalPermissionDenied
from .polices import ProposalPolicy
from .status_codes import PolicyFailure
from .validators import ProposalValidator
from decimal import Decimal, ROUND_HALF_UP
from typing import List
from uuid import UUID
import logging


logger = logging.getLogger("app_file")

GigModel = get_registered_model("collaboration", "Gig")
GigRoleModel = get_registered_model("collaboration", "GigRole")
GigCategoryModel = get_registered_model("collaboration", "Gigcategory")

Proposal = get_registered_model("collaboration", "Proposal")
ProposalRole = get_registered_model("collaboration", "ProposalRole")
ProposalDeliverable = get_registered_model("collaboration", "ProposalDeliverable")


def get_error_redirect(code: str, context: dict = None) -> str:
    """
    Maps failure codes to their respective redirect paths.
    Using a context dict allows for dynamic URL construction (IDs, etc).
    """
    context = context or {}

    mapping = {
        PolicyFailure.SUBSCRIPTION_REQUIRED.code: reverse_lazy(
            PaymentURLS.PAY_SUBSCRIPTION
        ),
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

    def __init__(self, user: AbstractUser, request):
        self.user = user
        self.request = request
        if not all([self.user, self.request]):
            raise Exception(
                f"Initialization failed: Both 'user' and 'request' are required. "
                f"Received: user={type(user).__name__}, request={type(request).__name__}"
            )

    def send_proposal(self, gig, payload: SendProposal, is_negotiating: bool):
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
            ProposalPolicy.ensure_can_apply(self.user, gig)
            ProposalValidator.validate(payload, gig)

            proposal = self.create_proposal_bundle(gig, payload, is_negotiating)
            self.notifications_flow(gig)

        except ProposalPermissionDenied as e:
            if e.code == PolicyFailure.SUBSCRIPTION_REQUIRED:
                e.redirect_url = get_error_redirect(e.code, {"gig_id": gig.id})
            raise e

        except Exception as e:
            import traceback
            traceback.print_exc()
            raise

        return proposal

    def modify_proposal_state(self, payload:ModifyProposalState):
        """User in this context is the project/gig creator"""

        try:
            proposal_role = self._get_proposal_role(payload.proposal_id, payload.role_id)
            proposal_obj = proposal_role.proposal
            ProposalPolicy.should_modify_state(self.user, proposal_obj, payload)
            self._transition_proposal_status(payload)

        except ProposalPermissionDenied as e:
            if e.code == PolicyFailure.SUBSCRIPTION_REQUIRED.code:
                e.redirect_url = get_error_redirect(e.code, {"gig_id": proposal_obj.gig})
            raise e
    
    def _get_proposal_role(self, proposal_id:UUID, proposal_role_id:UUID):
        proposal_role = (
            ProposalRole.objects
            .select_related("proposal", "proposal__gig")
            .filter(
                gig_role_id=proposal_role_id,
                proposal_id=proposal_id,
                proposal__gig__creator=self.user
            )
            .first()
        )

        if not proposal_role:
            raise ProposalPermissionDenied(
                message="We couldn't find that specific proposal in your project records. Please make sure you're accessing the correct link.",
                code=PolicyFailure.APPLICATION_RESTRICTED.code,
                title=PolicyFailure.APPLICATION_RESTRICTED.title
            )
        
        return proposal_role
        
    @transaction.atomic
    def create_proposal_bundle(self, gig, payload: SendProposal, is_negotiating: bool):
        gig = GigModel.objects.get(id=gig.id)
        proposal = self._create_proposal(
            gig, payload.proposal_value, payload.sent_at, is_negotiating
        )
        self._create_proposal_roles(gig, proposal, payload.applied_roles)
        self._create_deliverables(proposal, payload.deliverables)

    def _create_proposal(self, gig, proposal_value, sent_at, is_negotiating):
        ProposalModel = get_registered_model("collaboration", "Proposal")

        service_fee_rate = Decimal(str(SERVICE_FEE))
        precision = Decimal(str(DECIMAL_PLACE))

        excl_service_fee = (proposal_value / (Decimal('1') + service_fee_rate)).quantize(
            precision, rounding=ROUND_HALF_UP
        )
        
        try:
            proposal = ProposalModel.objects.create(
                gig=gig,
                sender=self.user,
                total_cost=excl_service_fee,
                sent_at=sent_at,
                is_negotiating=is_negotiating,
            )
            return proposal

        except IntegrityError as err:
            if getattr(err.__cause__, "args", None):
                db_error_code = err.__cause__.args[0]
                # MYSQL 1st then sqlite
                if db_error_code == 1062 or "UNIQUE constraint failed" in db_error_code:
                    message = (
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
                },
            )
            raise err

    def _get_role_object(self, gig, role_id):
        GigRoleModel = get_registered_model("collaboration", "GigRole")
        try:
            return gig.required_roles.get(role_id=role_id)
        except GigRoleModel.DoesNotExist:
            raise ProposalPermissionDenied(
                "It looks like this specific role isn't part of this project's current needs.",
                code=PolicyFailure.INVALID_ROLE.code,
                title=PolicyFailure.INVALID_ROLE.title,
            )
        except GigRoleModel.MultipleObjectsReturned:
            raise ProposalPermissionDenied(
                "There seems to be a configuration issue with this role.",
                code=PolicyFailure.INVALID_ROLE.code,
                title=PolicyFailure.INVALID_ROLE.title,
            )

    def _create_proposal_roles(self, gig, proposal, applied_roles: List[AppliedRoles]):
        role_instances = []
        role_obj = None

        for role_payload in applied_roles:
            if gig.has_gig_roles:
                try:
                    role_obj = gig.required_roles.get(role_id=role_payload.niche_id)
                except GigRoleModel.DoesNotExist:
                    raise ProposalPermissionDenied(
                        "It looks like this specific role isn't part of this project's current needs.",
                        code=PolicyFailure.INVALID_ROLE.code,
                        title=PolicyFailure.INVALID_ROLE.title,
                    )
                except GigRoleModel.MultipleObjectsReturned:
                    raise ProposalPermissionDenied(
                        "There seems to be a configuration issue with this role.",
                        code=PolicyFailure.INVALID_ROLE.code,
                        title=PolicyFailure.INVALID_ROLE.title,
                    )
                role_instances.append(
                    Proposal(
                        proposal=proposal,
                        gig_role=role_obj,
                        gig_category=None,
                        role_amount=role_payload.role_amount,
                        proposed_amount=role_payload.proposed_amount,
                        payment_plan=role_payload.payment_plan,
                    )
                )

            else:
                category_obj = GigCategoryModel.objects.get(
                    id=role_payload.niche_id, parent_id=role_payload.industry_id
                )
                
                Proposal.objects.create(
                    proposal=proposal,
                    gig_role=None,
                    gig_category=category_obj,
                    role_amount=role_payload.role_amount,
                    proposed_amount=role_payload.proposed_amount,
                    payment_plan=role_payload.payment_plan,
                )

        if gig.has_gig_roles:
            ProposalRole.objects.bulk_create(role_instances)

    def _create_deliverables(self, proposal, deliverables: List[DeliverablesPayload]):
        deliverable_instances = [
            ProposalDeliverable(
                proposal=proposal,
                sender=self.user,
                title=d.title,
                description=d.description,
                duration_unit=d.duration_unit,
                duration_value=d.duration_value,
                due_date=d.due_date,
                order=idx,
            )
            for idx, d in enumerate(deliverables)
        ]

        ProposalDeliverable.objects.bulk_create(deliverable_instances)
        
    @transaction.atomic
    def _transition_proposal_status(self, payload:ModifyProposalState):
        try:
            proposal_role = ProposalRole.objects.select_for_update().get(
                proposal_id=payload.proposal_id,
                gig_role_id=payload.role_id,
            )
        
            # comeback to
            proposal = Proposal.objects.select_for_update().get(
                id=payload.proposal_id
            )
            
            role_update_fields = []

            if proposal_role.status != payload.state:
                proposal_role.status = payload.state
                role_update_fields.append("status")

            if payload.state == ProposalRoleStatus.ACCEPTED:
                proposal_role.final_amount = (
                    proposal_role.proposed_amount or proposal_role.role_amount
                )
                role_update_fields.append("final_amount")

            if role_update_fields:
                proposal_role.save(update_fields=role_update_fields)
                
            if proposal.status != payload.state:
                proposal.status = payload.state

                # change gig_role to assign if gig has roles
                proposal.save(update_fields=["status"])
        
        except OperationalError:
            import traceback
            traceback.print_exc()
            raise ProposalError(
                message="This proposal is currently being updated by another action. Please wait a moment and try again.",
                title="Action in Progress",
            )
        
    def notifications_flow(self, gig):
        self._notify_creator_by_mail(gig)
        self._in_app_notifications(gig.creator)

    def _notify_creator_by_mail(self, gig) -> bool:
        from core.url_names import ProposalURLS
        
        if not gig.creator.is_verified:
            return False

        context = {
            "host": self.request.build_absolute_uri("/"),
            "project_title": gig.title,
            "project_proposal_url": self.request.build_absolute_uri(
                reverse_lazy(
                    ProposalURLS.PROPOSAL_LISTINGS,
                    kwargs={"gig_slug": gig.slug},
                )
            ),
            "num_of_proposals": gig.active_proposals_count,
        }

        resp = (
            EmailService(gig.creator.email)
                .set_subject(ProposalMails.Subjects.PROPOSAL_RECEIVED)
                .use_template(ProposalMails.PROPOSAL_RECEIVED)
                .with_context(**context)
                .send()
        )

        return resp

    def _in_app_notifications(self, creator: AbstractUser) -> None:
        """creates in-app notifications for both providers and creators"""
        # notify the both gig creator and service providers
        return None
