"""
Proposal state transition orchestration for the Servio platform.

Handles all lifecycle mutations of a Proposal and its associated roles —
withdrawal, rejection, and acceptance — enforcing policy checks and
atomicity guarantees before persisting any state change.
"""

from django.contrib.auth.models import AbstractUser
from django.db import transaction
from django.http import HttpRequest
from proposals.application.dto.modify_proposal_state import ModifyProposalState
from proposals.domain.policies.proposal_rules import ProposalPolicy
from proposals.domain.exceptions import ProposalPermissionDenied
from proposals.domain.status_codes import PolicyFailure
from proposals.infrastructure.repositories import ProposalRepository, ProposalRoleRepository
from proposals.models.choices import ProposalRoleStatus


class ProposalTransitionService:
    """
    Orchestrates validated state transitions for a Proposal and its roles.

    Enforces actor-level policy checks before delegating mutations to the
    appropriate repository layer. All transitions are executed atomically.
    """
    def __init__(self, user: AbstractUser, request: HttpRequest):
        """
        Binds the acting user, the current request, and the required repositories.

        Args:
            user: The authenticated user initiating the state change.
            request: The active HTTP request context.
        """
        self.actor = user
        self.request = request
        self.proposal_repository = ProposalRepository()
        self.role_repository = ProposalRoleRepository()
        
    def modify_state(self, data: ModifyProposalState):
        """
        Entry point for a proposal state transition request.

        Resolves the target proposal, enforces policy rules against the actor,
        then delegates to the internal mutation handler.

        Args:
            data: Validated payload containing the proposal ID, target role ID,
                  and the desired transition state.

        Raises:
            ProposalError: If the actor is not permitted to perform the transition.
        """
        proposal = self.proposal_repository.get_by_pk(proposal_id=data.proposal_id, to_entity=False)
        ProposalPolicy.check_proposal_action(self.actor, proposal, data)
        self._mutate_state(proposal, data)
    
    @transaction.atomic   
    def _mutate_state(self, proposal, data:ModifyProposalState):
        """
        Routes the transition to the correct handler based on the target state.

        Wrapped in a database transaction — if any step fails, all changes
        within the transition are rolled back.

        Args:
            proposal: The resolved Proposal ORM instance.
            data: The transition payload carrying state and role context.

        Raises:
            ValueError: If the target state has no registered transition handler.
        """
        match data.state:
            case ProposalRoleStatus.WITHDRAWN:
                self._withdraw_proposal(proposal)
            case ProposalRoleStatus.REJECTED:
                self._update_role_state(proposal, data, ProposalRoleStatus.REJECTED)
            case ProposalRoleStatus.ACCEPTED:
                self._update_role_state(proposal, data, ProposalRoleStatus.ACCEPTED)
                # generate contract
            case _:
                raise ProposalPermissionDenied(
                    "Unregcognized state/action on the requested proposal",
                    code=PolicyFailure.INVALID_ACTION.code,
                    title=PolicyFailure.INVALID_ACTION.title,
                )
        
    def _withdraw_proposal(self, proposal):
        """
        Withdraws all roles on a proposal and marks the proposal itself as withdrawn.

        Used when a provider pulls their entire proposal, regardless of individual
        role states. Affects all roles in a single operation.

        Args:
            proposal: The Proposal ORM instance to withdraw.
        """
        self.role_repository.withdraw_roles(proposal.roles)
        self.proposal_repository.withdraw_proposal(proposal)
    
    def _update_role_state(self, proposal, data: ModifyProposalState, role_status: ProposalRoleStatus) -> None:
        """
        Applies a status update to a single proposal role, then recalculates
        and persists the parent proposal's aggregate status.

        The proposal-level status is derived from the uniformity of its role
        statuses — if all roles share the same state it inherits that state,
        otherwise it is marked as REVIEWED.

        Args:
            proposal: The parent Proposal ORM instance.
            data: The transition payload, used to resolve the target role via role_id.
            role_status: The specific status to apply to the resolved role.
        """
        role = proposal.roles.get(role_id=data.role_id)
        role.status = role_status
        self.role_repository.update_status(role)
        self.proposal_repository.update_status(proposal, data.state)
