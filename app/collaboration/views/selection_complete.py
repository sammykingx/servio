from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.shortcuts import redirect
from django.views.generic import TemplateView
from core.url_names import AuthURLNames
from template_map.collaboration import Collabs
from registry_utils import get_registered_model
from uuid import UUID


class CompleteCollaborationView(LoginRequiredMixin, TemplateView):
    template_name = Collabs.SELECTION_COMPLETE
    
    def dispatch(self, request, *args, **kwargs):
        proposal_id = kwargs.get("proposal_id")
        self.proposal = self.get_validated_proposal(proposal_id)
        
        if not self.proposal:
            return redirect(AuthURLNames.ACCOUNT_DASHBOARD)
            
        return super().dispatch(request, *args, **kwargs)

    def get_validated_proposal(self, proposal_id):
        Proposal = get_registered_model("collaboration", "Proposal")
        try:
            return Proposal.objects.select_related(
                "gig", "gig__creator", "sender", "sender__profile"
            ).get(
                Q(sender=self.request.user) | Q(gig__creator=self.request.user),
                id=proposal_id
            )
        except (ObjectDoesNotExist, ValueError):
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        proposal = self.proposal
        
        context["gig_title"] = proposal.gig.title
        context["provider"] = proposal.sender
        context["prov_wame"] = self.get_url_message(proposal, proposal.sender)
        context["user_wame"] = self.get_url_message(proposal, self.request.user)
        context["is_provider"] = True if proposal.sender == self.request.user else False
        # context["whatsapp_number"] = proposal.sender.phone_number # Example
        # Add your other context fields here...
        
        return context
    
    def get_url_message(self, proposal, user):
        import urllib.parse
        
        message = (
            f"Hi {user.first_name.title()}, I'm reaching out regarding our project: "
            f"'{proposal.gig.title}'. Since we've agreed on the deliverables and the "
            "payment split, I'm excited to officially get started! "
            "Let's touch base here for real-time updates."
        )
        
        encoded_message = urllib.parse.quote(message)
        return f"https://wa.me/{user.profile.mobile_num}?text={encoded_message}"