from pydantic import BaseModel
from collaboration.models.choices import ProposalRoleStatus
from uuid import UUID


class ModifyProposalState(BaseModel):
    proposal_id: UUID
    role_id: UUID
    state: ProposalRoleStatus
    