from pydantic import BaseModel
from proposals.models.choices import ProposalRoleStatus
from uuid import UUID


class ModifyProposalState(BaseModel):
    proposal_id: UUID
    role_id: int
    state: ProposalRoleStatus
    re_assign: bool = False
    