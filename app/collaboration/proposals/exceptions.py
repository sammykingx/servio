"""
Domain-specific exceptions for proposal workflows.
===================
"""
from typing import Union

DEFAULT_TITLE ="Unable to Submit Proposal"

class ProposalError(Exception):
    """
    Base exception for all proposal-domain errors.
    
    This error is intended to be raised within views or outbound context 
    layers (e.g., API handlers or controllers) when a generic proposal 
    issue occurs that doesn't fit a specific subtype.

    Attributes:
        message (str): A human-readable error description.
        code (str, optional): A unique error code for programmatic handling.
        title (str): The category or title of the error, defaults to DEFAULT_TITLE.
        redirect_url( str | None): The url to redirect to for next line of action.
    """
    
    def __init__(self, message: str, *, code: str = None, title:str=DEFAULT_TITLE, redirect_url: Union[str, None]=None):
        self.message = message
        self.code = code
        self.title = title
        self.redirect_url = redirect_url
        super().__init__(message)

    def __str__(self) -> str:
        return self.message


class ProposalPermissionDenied(ProposalError):
    """
    Raised when an action violates proposal access control rules.
    
    This exception should be raised directly by permission-checking 
    classes or authorization logic when a user attempts an unauthorized 
    operation on a proposal.
    """
    pass


class ProposalValidationError(ProposalError):
    """
    Raised when a proposal fails business logic or data integrity checks.
    
    This exception should be raised by validator classes or service-layer 
    logic during the processing of proposal data to indicate that the 
    input is technically valid but logically rejected.
    """
    pass
