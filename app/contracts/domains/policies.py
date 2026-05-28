from django.contrib.auth.models import AbstractUser
from contracts.domains.entities import ContractEntity
from contracts.domains.errors import ContractPolicyFailure
from contracts.domains.exceptions import ContractPolicyViolation


class ContractPolicy:
    """
    Domain policy service for evaluating access control boundaries and 
    authorization permissions surrounding ContractEntity lifecycles.

    This class encapsulates pure business rules to determine if an active actor 
    holds the necessary legal or platform standing to view, modify, or execute 
    a given contract, acting as a defensive guard before infrastructure processing.
    """
    
    @staticmethod
    def _is_authorized_party(user:AbstractUser, contract: ContractEntity) -> bool:
        authorized_roles = [
            user == contract.client,
            user == contract.provider
        ]
        
        authorized = any(authorized_roles)
        
        if not authorized:
            raise ContractPolicyViolation(
                code=ContractPolicyFailure.NOT_AUTHORIZED.code,
                message="You are not an authorized party to this agreement.",
                title=ContractPolicyFailure.NOT_AUTHORIZED.title
            )
            
    @staticmethod
    def _has_signed(user: AbstractUser, contract: ContractEntity):
        if user == contract.client and contract.client_signed_at:
            raise ContractPolicyViolation(
                code=ContractPolicyFailure.ALREADY_SIGNED.code,
                message="You have already signed this agreement.",
                title=ContractPolicyFailure.ALREADY_SIGNED.title
            )
            
        if user == contract.provider and contract.provider_signed_at:
            raise ContractPolicyViolation(
                code=ContractPolicyFailure.ALREADY_SIGNED.code,
                message="You have already signed this agreement.",
                title=ContractPolicyFailure.ALREADY_SIGNED.title
            )
            
    @classmethod
    def check_signing_eligibility(cls, user: AbstractUser, contract: ContractEntity):
        cls._is_authorized_party(user, contract)
        cls._has_signed(user, contract)