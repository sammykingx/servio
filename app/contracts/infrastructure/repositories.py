from django.contrib.auth.models import AbstractUser
from django.db.models import Model
from django.utils.text import slugify
from django.utils import timezone
from contracts.domains.entities import ContractGenerationContext, ContractEntity
from core.model_registry import registry
from nanoid import generate
from typing import Union
from uuid6 import uuid7


class ContractRepository:
    def __init__(self):
        self.model = registry.Contract
    
    def get_by_id(self, contract_id):
        try:
            obj = self.model.objects.filter(id=contract_id).select_related(
                "project", "proposal", "provider", "provider__profile", "proposal_role"
            ).first()
            return obj
        except self.model.DoesNotExist:
            return None
        
    def _generate_reference(self) -> str:
        safe_characters = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        ref_id = f"srv_con_{generate(safe_characters, 22)}"
        return ref_id
    
    def _generate_slug(self, ref: str, role_name: str) -> str:
        base = slugify(f"{ref}-{role_name}")
        slug = f"{base}-{uuid7().hex[:12]}"
        return slug
    
    def _to_entity(self, contract: Model) -> ContractEntity:
        return ContractEntity(
            id=contract.id,
            reference=contract.reference,
            slug=contract.slug,
            proposal_id=contract.proposal_id,
            proposal_role_id=contract.proposal_role_id,
            project_id=contract.project_id,
            client=contract.client,
            provider=contract.provider,
            agreed_amount=contract.agreed_amount,
            currency=contract.currency,
            payment_plan=contract.payment_plan,
            status=contract.status,
            client_accepted_terms_at=contract.client_accepted_terms_at,
            client_paid_at=contract.client_paid_at,
            provider_accepted_terms_at=contract.provider_accepted_terms_at,
            completed_at=contract.completed_at
        )
        
    def create_contract(self, actor:AbstractUser, context: ContractGenerationContext) -> Model:
        ref = self._generate_reference()
        slug = self._generate_slug(ref, context.accepted_role.role_name)
        
        obj = self.model.objects.create(
            reference=ref,
            slug=slug,
            proposal=context.proposal,
            proposal_role=context.accepted_role,
            project=context.proposal.project,
            client=actor,
            provider=context.proposal.provider,
            agreed_amount=context.accepted_role.proposed_amount,
            currency=context.accepted_role.currency,
            payment_plan=context.accepted_role.payment_plan,
        )
        return obj
    
    def get_contract_by_reference(self, ref: str, as_entity: bool = True) -> Union[Model, ContractEntity]:
        try:
            obj = self.model.objects.filter(reference=ref).first()
            return self._to_entity(obj) if as_entity else obj
        
        except self.model.DoesNotExist:
            return None
        
    def persist_contract_acceptance(self, contract: ContractEntity, field_prefix: str) -> None:
        """
        Consolidated persistence for both client and provider.
        field_prefix should be 'client' or 'provider'.
        """
        update_field = f"{field_prefix}_accepted_terms_at"
        timestamp_value = getattr(contract, update_field)
        
        self.model.objects.filter(pk=contract.id).update(
            **{update_field: timestamp_value},
            status=contract.status,
            updated_at=timezone.now()
        )
    
    def persist_activation(self, contract: ContractEntity) -> None:
        self.model.objects.filter(pk=contract.id).update(
            status=contract.status,
            client_paid_at=contract.client_paid_at,
            updated_at=timezone.now()
        )
    