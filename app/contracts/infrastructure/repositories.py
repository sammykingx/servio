from django.contrib.auth.models import AbstractUser
from django.db.models import Model
from django.utils.text import slugify
from contracts.domains.entities import ContractGenerationContext, ContractEntity
from core.model_registry import registry
from datetime import datetime
from nanoid import generate
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
    
    def _tot_entity(self, contract: Model) -> ContractEntity:
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
            client_signed_at=contract.client_signed_at,
            provider_signed_at=contract.provider_signed_at,
            signed_at=contract.signed_at
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
    
    def get_contract_by_reference(self, ref: str, as_entity: bool = True) -> Model:
        try:
            obj = self.model.objects.filter(reference=ref).first()
            return self._tot_entity(obj) if as_entity else obj
        
        except self.model.DoesNotExist:
            return None
        
    def persist_provider_sign(self, contract: ContractEntity) -> Model:
        self.model.objects.filter(pk=contract.id).update(
            provider_signed_at=contract.provider_signed_at,
            status=contract.status,
            updated_at=datetime.now()
        )
    
    def persist_client_sign(self, contract: ContractEntity) -> Model:
        self.model.objects.filter(pk=contract.id).update(
            client_signed_at=contract.client_signed_at,
            status=contract.status,
            updated_at=datetime.now()
        )
    