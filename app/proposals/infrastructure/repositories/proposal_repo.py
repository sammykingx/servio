from core.model_registry import registry
from django.contrib.auth.models import AbstractUser
from django.db.models import Model
from proposals.domain.entities import ProjectEntity, ProposalEntity
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
    
    def _to_entity(self, proposal) -> ProposalEntity:
        return ProposalEntity(
            id=proposal.id,
            project=proposal.project,
            provider=proposal.provider,
            total_value=proposal.total_value,
            currency=proposal.currency,
            status=proposal.status,
            sent_at=proposal.sent_at,
            created_at=proposal.created_at
        )
