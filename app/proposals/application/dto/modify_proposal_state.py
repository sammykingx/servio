from pydantic import BaseModel
from proposals.models.choices import ProposalRoleStatus
from uuid import UUID


class ModifyProposalState(BaseModel):
    """
    Data transfer object (DTO) representing the frontend payload for modifying 
    the state of a specific proposal and it's role.

    This schema captures the primary key identifiers required to locate the target 
    records in the database, along with the desired state transition details.

    Attributes:
        proposal_id (UUID): The primary key identifier (`id`) of the target 
            `Proposal` record.
        role_id (int): The primary key identifier of the specific `ProposalRole` 
            record within the proposal.
        state (ProposalRoleStatus): The target status enum value being applied 
            to the proposal role (e.g., ACCEPTED, REJECTED, WITHDRAWN).
    """
    proposal_id: UUID
    role_id: int
    state: ProposalRoleStatus
    