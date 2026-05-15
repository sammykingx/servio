from core.model_registry import registry
from proposals.domain.entities import ProjectEntity, ProposalEntity
from django.contrib.auth.models import AbstractUser
from decimal import Decimal
from datetime import datetime


class ProposalRepository:
    def  __init__(self):
        self.model = registry.Proposal
        
    def create_proposal(self, *, project: ProjectEntity, provider: AbstractUser, value: Decimal, status: str, currency: str, sent_at: datetime) -> ProposalEntity:
        proposal = self.model.objects.create(
            project=project,
            provider=provider,
            total_value=value,
            currency=currency,
            status=status,
            sent_at=sent_at
        )
        return self._to_entity(proposal)
        
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
