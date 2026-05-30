from django.contrib.auth.models import AbstractUser
from contracts.domains.entities import ContractEntity


class ContractFundingService:
    """Service responsible for handling the funding process of a contract, including payment authorization and escrow management."""
    def __init__(self, actor: AbstractUser, contract: ContractEntity):
        self.actor = actor
        self.contract = contract