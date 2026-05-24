from core.model_registry import registry
from django.contrib.auth.models import AbstractUser
from django.db.models import Model
from django.utils import timezone
from proposals.domain.entities import ProposalEntity, ProposalRoleEntity
from proposals.models.choices import ProposalStatus
from proposals.domain.status_codes import PolicyFailure
from proposals.domain.exceptions import ProposalError
from decimal import Decimal
from datetime import datetime
from uuid import UUID
from typing import Union


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
    
    def get_by_pk(self, proposal_id:UUID, to_entity=True) -> Union[ProposalEntity, Model]:
        try:
            proposal = (
                self.model.objects
                .filter(pk=proposal_id)
                .prefetch_related("roles")
                .first()
            )
            return self._to_entity(proposal) if to_entity else proposal
            
        except self.model.DoesNotExist:
            raise ProposalError(
                "The requested proposal could not be loaded.",
                code=PolicyFailure.INVALID_OBJECT.code,
                title=PolicyFailure.INVALID_OBJECT.title,
            )
            
    def withdraw_proposal(self, proposal:ProposalEntity) -> None:
        self.model.objects.filter(pk=proposal.id).update(
            status=ProposalStatus.WITHDRAWN,
            updated_at=timezone.now()
        )
    
    def update_status(self, proposal, state: ProposalStatus) -> None:
        """
        Evaluates the child roles of a proposal and updates the proposal's status 
        in memory and inside the database.

        If every associated proposal role status matches the target state, the 
        proposal's status transitions directly to that target state. Otherwise, 
        the proposal's status falls back to `ProposalStatus.REVIEWED`. 
        
        Changes are only saved to the database if a state transition occurs.

        Args:
            proposal (DjangoProposalModel): An instance of the Django `Proposal` model.
            state (ProposalStatus): The target status value being applied 
                to the proposal ecosystem.

        Returns:
            None

        Raises:
            self.model.DoesNotExist: If the proposal ID found on the domain entity 
                does not match any record in the database.
        """
        all_roles_match = not proposal.roles.exclude(status=state).exists()
        new_status = state if all_roles_match else ProposalStatus.REVIEWED
        self.model.objects.filter(pk=proposal.id).update(
            status=new_status, updated_at=timezone.now()
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
