from django.db.models import Model
from core.model_registry import registry
from collaboration.models.choices import PaymentOption
from proposals.domain.entities import ProposalEntity
from proposals.models.choices import ProposalRoleStatus
from decimal import Decimal
from typing import Union, Literal


class ProposalRoleRepository:
    def __init__(self):
        self.model = registry.ProposalRole
        
    def create_roles(
        self,
        *,
        proposal: ProposalEntity,
        proposed_amount: Decimal,
        currency: Literal["NGN", "USD"],
        payment_plan: PaymentOption, 
        role: Union[int, None] = None,
        category: Union[int, None] = None,
        client_budget: Union[Decimal, None] = None
    ) -> Model:
        obj = self.model.objects.create(
            proposal=proposal,
            role=role,
            category=category,
            client_budget=client_budget,
            proposed_amount=proposed_amount,
            currency=currency,
            payment_plan=payment_plan,
        )
        
        return obj