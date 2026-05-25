from django.contrib.auth.models import AbstractUser
from django.db.models import Model
from django.utils.text import slugify
from contracts.domains.entities import ContractGenerationContext
from core.model_registry import registry
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
    
    def _generate_reference(self) -> str:
        safe_characters = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        ref_id = f"srv_con{generate(safe_characters, 18)}"
        return ref_id
    
    def _generate_slug(self, ref: str, role_name: str) -> str:
        base = slugify(f"{ref}-{role_name}")
        slug = f"{base}-{uuid7().hex[:12]}"
        return slug