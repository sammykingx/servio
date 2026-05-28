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
    def _has_accepted_terms(user: AbstractUser, contract: ContractEntity):
        client_has_accepted = (user == contract.client and contract.client_accepted_terms_at)
        provider_has_accepted = (user == contract.provider and contract.provider_accepted_terms_at)

        if client_has_accepted or provider_has_accepted:
            raise ContractPolicyViolation(
                code=ContractPolicyFailure.TERMS_ALREADY_ACCEPTED.code,
                message="You have already accepted the terms of this agreement.",
                title=ContractPolicyFailure.TERMS_ALREADY_ACCEPTED.title
            )
            
    @classmethod
    def check_signing_eligibility(cls, user: AbstractUser, contract: ContractEntity):
        cls._is_authorized_party(user, contract)
        cls._has_accepted_terms(user, contract)