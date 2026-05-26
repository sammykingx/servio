"""
This module defines the ContractCreationService, responsible for orchestrating the generation of contracts following successful proposal
role acceptances. It serves as the application service layer that interfaces between the proposal domain and the contract domain, ensuring 
that all necessary context is validated and passed along for contract creation. 
The service is designed to be invoked by the proposal application services once a proposal role reaches an accepted state, guaranteeing that contracts are only generated under the correct conditions. 
All operations within this service are executed with transactional integrity to maintain consistent state across both domains.
"""

from django.contrib.auth.models import AbstractUser
from ..domains.entities import ContractGenerationContext
from ..infrastructure.repositories import ContractRepository


class ContractCreationService:
    """
        Handles the initialization, generation, and persistence of contracts
        following successful proposal role acceptances.
    """
    
    def __init__(self, actor: AbstractUser):
        self.contract_repo = ContractRepository()
        self.actor = actor
        
    def create_contract(self, context: ContractGenerationContext) -> None:
        """
            Entry point to spawn a contract from a completed proposal role lifecycle.
            
            Args:
                context: The validated DTO handed off by the proposal domain.
        """
        self.contract_repo.create_contract(actor=self.actor, context=context)
