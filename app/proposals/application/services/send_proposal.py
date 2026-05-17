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
from proposals.application.dto.send_proposal import ProposalSubmissionPayload
from proposals.application.dto.modify_proposal_state import ModifyProposalState
from services.email_service import EmailService
from template_map.emails import ProposalMails
from proposals.domain.entities import ProjectEntity
from proposals.domain.exceptions import ProposalError, ProposalPermissionDenied
from proposals.domain.policies.proposal_rules import ProposalPolicy
from proposals.domain.status_codes import PolicyFailure
from proposals.domain.validators import ProposalValidator
from proposals.infrastructure.repositories import (
    ProjectRepository, ProposalRepository, ProposalRoleRepository, 
    ProjectDeliverablesRepository
)
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
        self.role_repository = ProposalRoleRepository()
        self.deliverables_repo = ProjectDeliverablesRepository()

    def submit_proposal(self, payload: ProposalSubmissionPayload):
        """
        Validates, persists, and orchestrates notifications for a new project proposal submission.
        """
        try:
            project = self.project_repository.get_by_id(project_id=payload.project_id)
            ProposalPolicy.ensure_can_apply(self.actor, project)
            ProposalValidator.validate(payload, project)

            proposal = self._create_proposal_bundle(payload)
            self.notifications_flow(project)
            return proposal

        except ProposalPermissionDenied as e:
            if e.code == PolicyFailure.SUBSCRIPTION_REQUIRED.code:
                e.redirect_url = get_error_redirect(e.code)
            raise e
        
    @transaction.atomic
    def _create_proposal_bundle(self, payload: ProposalSubmissionPayload):
        """
        Persists the entire Proposal, Roles, and Deliverables tree in exactly 
        3 SQL insert transactions. Safe for resource-constrained cPanel environments.
        """
        try:
            project = self.project_repository.get_by_id(
                project_id=payload.project_id, with_lock=True, as_entity=False
            )
            proposal = self.proposal_repository.create_proposal(
                project=project,
                provider=self.actor,
                value=payload.total_value,
                currency=payload.currency,
                sent_at=payload.sent_at
            )
            for applied_role in payload.applied_roles:
                role_fk_id = applied_role.niche_id if project.has_gig_roles else None
                category_fk_id = None if project.has_gig_roles else applied_role.niche_id
                
                saved_role = self.role_repository.create_roles(
                    proposal=proposal,
                    role=role_fk_id,
                    category=category_fk_id,
                    client_budget=None,
                    proposed_amount=applied_role.role_amount,
                    currency=applied_role.currency,
                    payment_plan=applied_role.payment_plan,
                )
                self.deliverables_repo.bulk_create_from_payload(
                    saved_role, self.actor, applied_role.deliverables
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
