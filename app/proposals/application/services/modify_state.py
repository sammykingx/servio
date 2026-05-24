from django.contrib.auth.models import AbstractUser
from django.http import HttpRequest
from proposals.infrastructure.repositories import ProposalRepository, ProposalRoleRepository
from proposals.application.dto.modify_proposal_state import ModifyProposalState
from proposals.domain.policies.proposal_rules import ProposalPolicy


class ProposalTransitionService:
    def __init__(self, user: AbstractUser, request: HttpRequest):
        self.actor = user
        self.request = request
        self.proposal_repository = ProposalRepository()
        self.role_repository = ProposalRoleRepository()
        
    def modify_state(self, data: ModifyProposalState):
        proposal = self.proposal_repository.get_by_id(proposal_id=data.proposal_id)
        ProposalPolicy.should_modify_state(self.actor, proposal, data)
        
    def withdraw_proposal(self):
        pass
    
    # @transaction.atomic
    # def _transition_proposal_status(self, payload:ModifyProposalState):
    #     try:
    #         proposal_role = ProposalRole.objects.select_for_update().get(
    #             proposal_id=payload.proposal_id,
    #             gig_role_id=payload.role_id,
    #         )
        
    #         # comeback to
    #         proposal = Proposal.objects.select_for_update().get(
    #             id=payload.proposal_id
    #         )
            
    #         role_update_fields = []

    #         if proposal_role.status != payload.state:
    #             proposal_role.status = payload.state
    #             role_update_fields.append("status")

    #         if payload.state == ProposalRoleStatus.ACCEPTED:
    #             proposal_role.final_amount = (
    #                 proposal_role.proposed_amount or proposal_role.role_amount
    #             )
    #             role_update_fields.append("final_amount")

    #         if role_update_fields:
    #             proposal_role.save(update_fields=role_update_fields)
                
    #         if proposal.status != payload.state:
    #             proposal.status = payload.state

    #             # change gig_role to assign if gig has roles
    #             proposal.save(update_fields=["status"])
        
    #     except OperationalError:
    #         import traceback
    #         traceback.print_exc()
    #         raise ProposalError(
    #             message="This proposal is currently being updated by another action. Please wait a moment and try again.",
    #             title="Action in Progress",
    #         )
        
    # def modify_proposal_state(self, payload:ModifyProposalState):
    #     """User in this context is the project/project creator"""

    #     try:
    #         proposal_role = self._get_proposal_role(payload.proposal_id, payload.role_id)
    #         proposal_obj = proposal_role.proposal
    #         ProposalPolicy.should_modify_state(self.actor, proposal_obj, payload)
    #         self._transition_proposal_status(payload)

    #     except ProposalPermissionDenied as e:
    #         if e.code == PolicyFailure.SUBSCRIPTION_REQUIRED.code:
    #             e.redirect_url = get_error_redirect(e.code, {"gig_id": proposal_obj.gig})
    #         raise e
    
    # def _get_proposal_role(self, proposal_id:UUID, proposal_role_id:UUID):
    #     proposal_role = (
    #         ProposalRole.objects
    #         .select_related("proposal", "proposal__gig")
    #         .filter(
    #             gig_role_id=proposal_role_id,
    #             proposal_id=proposal_id,
    #             proposal__gig__creator=self.actor
    #         )
    #         .first()
    #     )

    #     if not proposal_role:
    #         raise ProposalPermissionDenied(
    #             message="We couldn't find that specific proposal in your project records. Please make sure you're accessing the correct link.",
    #             code=PolicyFailure.APPLICATION_RESTRICTED.code,
    #             title=PolicyFailure.APPLICATION_RESTRICTED.title
    #         )
        
    #     return proposal_role