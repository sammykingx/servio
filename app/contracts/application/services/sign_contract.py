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
    
    def accept_contract_terms(self, contract: ContractEntity) -> None:
        ContractPolicy.check_signing_eligibility(self.actor, contract)
        role_map = {
            contract.provider: ("provider_accepted_terms", "provider"),
            contract.client: ("client_accepted_terms", "client"),
        }

        action_method_name, field_prefix = role_map.get(self.actor, (None, None))

        if action_method_name:
            getattr(contract, action_method_name)()
            self.contract_repo.persist_contract_acceptance(contract, field_prefix)  
