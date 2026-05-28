from pydantic import BaseModel


class SignContractDTO(BaseModel):
    """
    Data Transfer Object validating complete legal acceptance from a contract party.

    This schema ensures that a user (whether Client or Provider) has explicitly 
    checked every required acknowledgment box. If any boolean field is False, 
    validation fails, indicating incomplete consent to the contract terms.
    """
    # contract_ref: str
    terms_acknowledged: bool
    policy_acknowledged: bool
    automated_payout_accepted: bool
