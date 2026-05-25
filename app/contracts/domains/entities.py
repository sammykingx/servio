from dataclasses import dataclass
from django.db.models import Model


@dataclass(frozen=True)
class ContractGenerationContext:
    """
    An immutable DTO representing the verified context handed off 
    from the Proposal service to the Contract service.
    """
    proposal: Model
    accepted_role: Model
