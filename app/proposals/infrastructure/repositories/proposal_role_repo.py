from core.model_registry import registry
from collaboration.models.choices import PaymentOption
from proposals.domain.entities import ProposalEntity
from proposals.models.choices import ProposalRoleStatus
from decimal import Decimal


class ProposalRoleRepository:
    def __init__(self):
        self.model = registry.ProposalRole
        
    def create_roles(
        self, 
        proposal: ProposalEntity,
        amount: Decimal, 
        status: ProposalRoleStatus, 
        payment_plan: PaymentOption, 
        role=None,
        category=None
    ):
        pass