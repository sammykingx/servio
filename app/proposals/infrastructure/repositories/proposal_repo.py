from core.model_registry import registry
from django.contrib.auth.models import AbstractUser
from django.db.models import Model
from proposals.domain.entities import ProposalEntity, ProposalRoleEntity
from proposals.models.choices import ProposalStatus
from proposals.domain.status_codes import PolicyFailure
from proposals.domain.exceptions import ProposalError
from decimal import Decimal
from datetime import datetime
from uuid import UUID


class ProposalRepository:
    def  __init__(self):
        self.model = registry.Proposal
        
    def create_proposal(
        self,
        *, 
        project: Model, 
        provider: AbstractUser, 
        value: Decimal, 
        currency: str,
        sent_at: datetime
    ) -> Model:
        proposal = self.model.objects.create(
            project=project,
            provider=provider,
            total_value=value,
            currency=currency,
            sent_at=sent_at
        )
        return proposal
    
    def get_by_id(self, proposal_id:UUID) ->ProposalEntity:
        try:
            proposal = (
                self.model.objects
                .filter(id=proposal_id)
                .prefetch_related("roles")
                .first()
            )
            return self._to_entity(proposal)
            
        except self.model.DoesNotExist:
            raise ProposalError(
                "The requested proposal could not be loaded.",
                code=PolicyFailure.INVALID_OBJECT.code,
                title=PolicyFailure.INVALID_OBJECT.title,
            )
            
    def update_status(self, proposal:ProposalEntity) -> None:
        self.model.objects.filter(id=proposal.id).update(
            status=proposal.status
        )
        
    def _to_entity(self, proposal) -> ProposalEntity:
        prop_roles =[
            ProposalRoleEntity(
                id=prop_role.id,
                role_fk=prop_role.role_id,
                category_fk=prop_role.category_id,
                client_budget=prop_role.client_budget,
                proposed_amount=prop_role.proposed_amount,
                currency=prop_role.currency,
                payment_plan=prop_role.payment_plan,
                status=prop_role.status
            )
            for prop_role in proposal.roles.all()
        ]
        return ProposalEntity(
            id=proposal.id,
            project=proposal.project,
            provider=proposal.provider,
            total_value=proposal.total_value,
            currency=proposal.currency,
            status=proposal.status,
            sent_at=proposal.sent_at,
            created_at=proposal.created_at,
            roles=prop_roles
        )
