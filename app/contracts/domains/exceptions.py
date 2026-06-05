from typing import Union


DEFAULT_TITLE = "Unable to Process Contract"


class ContractException(Exception):
    """Base exception for contract-related errors."""
    def __init__(
        self,
        message: str,
        *,
        code: str = None,
        title: str = DEFAULT_TITLE,
        redirect_url: Union[str, None] = None,
    ):
        self.message = message
        self.code = code
        self.title = title
        self.redirect_url = redirect_url
        super().__init__(message)

    def __str__(self) -> str:
        return self.message
    
    
class ContractPolicyViolation(ContractException):
    pass

class ContractPaymentVerificationFailure(ContractException):
    def __init__(self, message="No successful payment record found for this contract."):
        self.code = "PAYMENT_NOT_VERIFIED"
        self.title = "Payment Required"
        super().__init__(message)