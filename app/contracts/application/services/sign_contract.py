from django.db.models import Model
from django.contrib.auth.models import AbstractUser
from contracts.infrastructure.repositories import ContractRepository
from contracts.domains.entities import ContractEntity
from contracts.domains.policies import ContractPolicy


class ContractSigningService:
    def __init__(self, user: AbstractUser):
        self.actor = user
        self.contract_repo = ContractRepository()
        
    def to_entity(self, contract: Model) -> ContractEntity:
        return ContractEntity.from_model(contract)
    
    def sign_contract(self, contract: ContractEntity) -> None:
        ContractPolicy.check_signing_eligibility(self.actor, contract)
        if contract.provider == self.actor:
            contract.provider_sign()
            self.contract_repo.persist_provider_sign(contract)
            
        # elif contract.client == self.actor:
        #     contract.client_signed()