from django.db.models import Model
from core.model_registry import registry
from collaboration.models.choices import PaymentOption
from proposals.domain.entities import ProposalRoleEntity
from proposals.models.choices import ProposalRoleStatus
from decimal import Decimal
from typing import Union, Literal, List, TypeVar
from uuid import UUID


ProposalRoleModelT = TypeVar("ProposalRole")


class ProposalRoleRepository:
    def __init__(self):
        self.model = registry.ProposalRole
        
    def create_roles(
        self,
        *,
        proposal: Model,
        proposed_amount: Decimal,
        currency: Literal["NGN", "USD"],
        payment_plan: PaymentOption, 
        role_instance: Union[int, None] = None,
        category_instance: Union[int, None] = None,
        client_budget: Union[Decimal, None] = None
    ) -> Model:
        obj = self.model.objects.create(
            proposal=proposal,
            role=role_instance,
            category=category_instance,
            client_budget=client_budget,
            proposed_amount=proposed_amount,
            currency=currency,
            payment_plan=payment_plan,
        )
        
        return obj
    
    def get_by_id(self, role_id: UUID, ) -> Union[ProposalRoleEntity, Model]:
        """Fetches a ProposalRole model and maps it to its pure domain entity."""
        try:
            db_obj = (
                self.model.objects
                # .select_related("proposal")
                .get(id=role_id)
            )
            return self._to_entity(db_obj)
        except self.model.DoesNotExist:
            return None
        
    def update_status(self, role_instance) -> None:
        """Persists the ProposalRole instance 'role_instance' status modification back to the database."""
        self.model.objects.filter(id=role_instance.id).update(status=role_instance.status)
        
    def withdraw_roles(self, roles:List[ProposalRoleModelT]):
        for role in roles:
            role.status = ProposalRoleStatus.WITHDRAWN
        self.model.objects.bulk_update(roles, fields=["status"])
        
    def _to_entity(self, role_obj) -> ProposalRoleEntity:
        return ProposalRoleEntity(
            id=role_obj.id,
            role_fk=role_obj.role_id,
            category_fk=role_obj.category_id,
            client_budget=role_obj.client_budget,
            proposed_amount=role_obj.proposed_amount,
            currency=role_obj.currency,
            payment_plan=role_obj.payment_plan,
            status=role_obj.status
        )
