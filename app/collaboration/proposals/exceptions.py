"""
Domain-specific exceptions for proposal workflows.
"""

DEFAULT_TITLE ="Unable to Submit Proposal"

class ProposalError(Exception):
    """Base class for proposal-related errors."""
    
    def __init__(self, message: str, *, code: str = None, title=DEFAULT_TITLE):
        self.message = message
        self.code = code
        self.title = title
        super().__init__(message)

    def __str__(self):
        return self.message


class ProposalPermissionDenied(ProposalError):
    """Raised when a user is not allowed to submit a proposal."""
    pass


class ProposalValidationError(ProposalError):
    """Raised when proposal business validation fails."""
    pass
