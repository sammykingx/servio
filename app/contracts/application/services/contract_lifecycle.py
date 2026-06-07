from django.db.models import Model
from django.contrib.auth.models import AbstractUser
from core.model_registry import registry
from contracts.infrastructure.repositories import ContractRepository
from contracts.domains.entities import ContractEntity, ContractActivationResult
from contracts.domains.exceptions import ContractPaymentVerificationFailure
from contracts.domains.policies import ContractPolicy
from payments.domain.enums import PaymentStatus


class ContractLifecycleService:
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
            
    def activate_contract(self, contract_obj:Model) -> ContractActivationResult:
        contract = ContractEntity.from_model(contract_obj)
        ContractPolicy.check_activation_eligibility(self.actor, contract)
        payment = registry.Payment.objects.filter(
            contract_ref=contract.reference,
            user=self.actor,
            status=PaymentStatus.SUCCESS
        ).first()
        
        if not payment:
            raise ContractPaymentVerificationFailure(
                f"Cannot activate contract {contract.reference}. Payment has not been verified successfully."
            )
        if not contract.client_paid_at:
            contract.mark_as_paid_by_client(paid_at=payment.paid_at)
            self.contract_repo.persist_activation(contract)
            
        return ContractActivationResult(
            contract=contract,
            payment=payment
        )
