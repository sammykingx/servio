from typing import NamedTuple


class ContractFailureDetail(NamedTuple):
    """
    A structured representation of a domain failure.

    Attributes:
        code (str): A unique, machine-readable string identifier (e.g., 'INVALID_CONTRACT').
        title (str): A brief, human-readable description intended for end-user display.
    """

    code: str
    title: str
    
    
class ContractPolicyFailure:
    """
    Constants representing authorization and business policy violations specific to contract operations.

    These codes are triggered when a user or action violates the fundamental
    rules of contract management, such as signing restrictions, status constraints,
    or role-based permissions.
    """

    INVALID_CONTRACT = ContractFailureDetail("INVALID_CONTRACT", "Contract Not Found")
    NOT_AUTHORIZED = ContractFailureDetail("NOT_AUTHORIZED", "Unauthorized Action")
    ALREADY_SIGNED = ContractFailureDetail("ALREADY_SIGNED", "Contract Already Signed")
    TERMS_NOT_ACKNOWLEDGED = ContractFailureDetail(
        "TERMS_NOT_ACKNOWLEDGED", "Terms Acknowledgment Required"
    )
    POLICY_NOT_ACKNOWLEDGED = ContractFailureDetail(
        "POLICY_NOT_ACKNOWLEDGED", "Policy Acknowledgment Required"
    )