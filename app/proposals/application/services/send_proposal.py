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
from django.db import transaction, IntegrityError, OperationalError
from django.http import HttpRequest
from django.urls import reverse_lazy
from core.model_registry import registry
from core.url_names import PaymentURLS
from proposals.models.choices import ProposalRoleStatus
from proposals.application.dto.send_proposal import (
    ProposedRole,
    ProposalDeliverable,
    ProposalSubmissionPayload,
)
from proposals.application.dto.modify_proposal_state import ModifyProposalState
from constants import SERVICE_FEE, DECIMAL_PLACE
from services.email_service import EmailService
from template_map.emails import ProposalMails
from proposals.domain.entities import ProjectEntity
from proposals.domain.exceptions import ProposalError, ProposalPermissionDenied, ProposalPersistenceError
from proposals.domain.policies.proposal_rules import ProposalPolicy
from proposals.domain.status_codes import PolicyFailure
from proposals.domain.validators import ProposalValidator
from proposals.infrastructure.repositories import ProjectRepository, ProposalRepository
from decimal import Decimal, ROUND_HALF_UP
from typing import List
from uuid import UUID
import logging


logger = logging.getLogger("app_file")

GigModel = registry.Gig
GigRoleModel = registry.GigRole
GigCategoryModel = registry.GigCategory

Proposal = registry.Proposal
ProposalRole = registry.ProposalRole
ProposalDeliverable = registry.ProposalDeliverable


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


class ProposalOrchestrationService:
    """
    Domain Service for orchestrating the Proposal lifecycle.

    This service acts as the (conductor), coordinating between
    Policies, Validators, and Persistence layers. It ensures that
    proposals are only created when all business and integrity
    constraints are satisfied.
    """

    def __init__(self, actor: AbstractUser, request: HttpRequest):
        self.actor = actor
        self.request = request
        self.project_repository = ProjectRepository()
        self.proposal_repository = ProposalRepository()
        # self.role_repository = ProposalRoleRepository()
        # self.deliverable_repository = ProposalDeliverableRepository()

    def submit_proposal(self, payload: ProposalSubmissionPayload, is_negotiating: bool):
        try:
            project = self.project_repository.get_by_id(project_id=payload.project_id)
            ProposalPolicy.ensure_can_apply(self.actor, project)
            ProposalValidator.validate(payload, project)
            # validate if the roles belong to the project

            proposal = self.create_proposal_bundle(payload)
            self.notifications_flow(project)

        except ProposalPermissionDenied as e:
            if e.code == PolicyFailure.SUBSCRIPTION_REQUIRED.code:
                e.redirect_url = get_error_redirect(e.code)
            raise e

        except ProposalError:
            raise

        except Exception as e:
            # import traceback
            # traceback.print_exc()
            raise

        return proposal
        
    @transaction.atomic
    def create_proposal_bundle(self, payload: ProposalSubmissionPayload):
        try:
            project = self.project_repository.get_by_id(project_id=payload.project_id, with_lock=True)
            proposal = self.proposal_repository.create_proposal(
                project=project,
                provider=self.actor,
                value=payload.total_value,
                currency=payload.currency,
                sent_at=payload.sent_at
            )
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
                    "user_id": str(self.actor.id),
                    "gig_id": str(project.id),
                },
            )
            raise err
        
        self._create_proposal_roles(project, proposal, payload.applied_roles)
        self._create_deliverables(proposal, payload.deliverables)

    def _get_role_object(self, gig, role_id):
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

    def _create_proposal_roles(self, gig, proposal, applied_roles: list):
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

    def _create_deliverables(self, proposal, deliverables: list):
        deliverable_instances = [
            ProposalDeliverable(
                proposal=proposal,
                sender=self.actor,
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

    def _notify_creator_by_mail(self, project: ProjectEntity) -> bool:
        from core.url_names import ProposalURLS
        
        if not project.creator.is_verified:
            return False

        context = {
            "host": self.request.build_absolute_uri("/"),
            "project_title": project.title,
            "project_proposal_url": self.request.build_absolute_uri(
                reverse_lazy(
                    ProposalURLS.PROPOSAL_LISTINGS,
                    kwargs={"project_slug": project.slug},
                )
            ),
            "num_of_proposals": project.active_proposals_count,
        }

        resp = (
            EmailService(project.creator.email)
                .set_subject(ProposalMails.Subjects.PROPOSAL_RECEIVED)
                .use_template(ProposalMails.PROPOSAL_RECEIVED)
                .with_context(**context)
                .send()
        )

        return resp

    def _in_app_notifications(self, creator: AbstractUser) -> None:
        """creates in-app notifications for both providers and creators"""
        # notify the both project creator and service providers
        return None
    
    def modify_proposal_state(self, payload:ModifyProposalState):
        """User in this context is the project/project creator"""

        try:
            proposal_role = self._get_proposal_role(payload.proposal_id, payload.role_id)
            proposal_obj = proposal_role.proposal
            ProposalPolicy.should_modify_state(self.actor, proposal_obj, payload)
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
                proposal__gig__creator=self.actor
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
    
    # -------------------------------
    # def _create_proposal(self, gig, proposal_value, sent_at, is_negotiating):
    #     service_fee_rate = Decimal(str(SERVICE_FEE))
    #     precision = Decimal(str(DECIMAL_PLACE))

    #     excl_service_fee = (proposal_value / (Decimal('1') + service_fee_rate)).quantize(
    #         precision, rounding=ROUND_HALF_UP
    #     )
        
    #     try:
    #         proposal = Proposal.objects.create(
    #             gig=gig,
    #             provider=self.actor,
    #             total_cost=excl_service_fee,
    #             sent_at=sent_at,
    #         )
    #         return proposal

    #     except IntegrityError as err:
    #         if getattr(err.__cause__, "args", None):
    #             db_error_code = err.__cause__.args[0]
    #             # MYSQL 1st then sqlite
    #             if db_error_code == 1062 or "UNIQUE constraint failed" in db_error_code:
    #                 message = (
    #                     "It looks like you’ve already shared your "
    #                     "vision for this project!. Sit tight whilst "
    #                     "the previous proposal is been reviewed."
    #                 )
    #                 raise ProposalPermissionDenied(
    #                     message,
    #                     code=PolicyFailure.DUPLICATE_APPLICATION.code,
    #                     title=PolicyFailure.DUPLICATE_APPLICATION.title,
    #                 )
    #         logger.error(
    #             "Unexpected IntegrityError during proposal creation",
    #             extra={
    #                 "user_id": str(self.actor.id),
    #                 "gig_id": str(gig.id),
    #             },
    #         )
    #         raise err
