# Custom exceptions for payments domain.

class DomainException(Exception):
    """Base class for all business logic errors."""
    def __init__(self, message: str,*, code: str, title: str):
        self.message = message
        self.code = code
        self.title = title
        super().__init__(self.message)

class PolicyViolationError(DomainException):
    """Raised when a PolicyFailure constant is violated."""
    pass
