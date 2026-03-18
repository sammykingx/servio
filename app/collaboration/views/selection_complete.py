from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.shortcuts import redirect
from django.views.generic import TemplateView
from core.url_names import AuthURLNames
from template_map.collaboration import Collabs
from registry_utils import get_registered_model
from uuid import UUID
import urllib.parse


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
        is_creator = self.proposal.sender == self.request.user
        if is_creator:
            # creator -> provider
            whatsapp_msg = self.get_url_message(self.proposal, self.request.user, is_creator)
        else:
            whatsapp_msg = self.get_url_message(self.proposal, self.proposal.sender, is_creator)
        
        context["gig_title"] = self.proposal.gig.title
        context["provider"] = self.proposal.sender
        context["wa_msg"] = whatsapp_msg
        # context["whatsapp_number"] = proposal.sender.phone_number # Example
        # Add your other context fields here...
        
        return context
    
    def get_url_message(self, proposal, recipient: AbstractUser, is_creator: bool):
        project_title = proposal.gig.title

        if is_creator:
            # Creator → Provider
            message = (
                f"Hi {recipient.first_name.title()},\n\n"
                f"I'm reaching out regarding our project *\"{project_title}\"* on *Servio*.\n\n"
                "We've aligned on the deliverables and payment structure, and I'm looking forward "
                "to getting started with you.\n\n"
                "Feel free to use this chat for updates, coordination, and any questions along the way.\n\n"
                "_— Sent via *Servio* by DivGM_"
            )
        else:
            # Provider → Creator
            message = (
                f"Hi {recipient.first_name.title()},\n\n"
                f"I'm reaching out regarding our project *\"{project_title}\"* on *Servio*.\n\n"
                "Everything looks good on my end regarding the deliverables and payment terms, "
                "and I'm ready to get started.\n\n"
                "Happy to coordinate here for updates and next steps.\n\n"
                "_— Sent via *Servio* by DivGM_"
            )

        encoded_message = urllib.parse.quote(message)
        return f"https://wa.me/{recipient.profile.mobile_num}?text={encoded_message}"
    
    def get_mailto_url(self, proposal, sender:AbstractUser, recipient:AbstractUser):
        project_title = proposal.gig.title
        sender_name = sender.first_name.title()
        recipient_name = recipient.first_name.title()
        subject = f"Project Kickoff: {project_title} (via Servio)"

        is_creator = sender == proposal.gig.creator

        # Get timeline summary (your existing method)
        timeline = proposal.timeline_summary()

        # Optional: include deliverables summary
        deliverables = proposal.deliverables.all()
        deliverables_list = "\n".join(
            [f"- {d.title} (Due: {d.due_date})" for d in deliverables]
        ) if deliverables else "No deliverables specified."


        if is_creator:
            body = f"""
                Hi {recipient_name},

                I hope you're doing well.

                I'm reaching out to officially kick off our collaboration on the project "{project_title}" via Servio.

                We've aligned on the scope, deliverables, and payment structure, and I'm excited to begin working with you.

                Project Summary:
                - Project: {project_title}
                - Timeline: {timeline}

                Deliverables:
                {deliverables_list}

                You can use this email or WhatsApp for communication, but feel free to suggest your preferred workflow.

                Looking forward to a smooth and successful collaboration.

                Best regards,  
                {sender_name}

                —
                Sent via Servio by DivGM
                """
        else:
            body = f"""
                Hi {recipient_name},

                I hope you're doing well.

                I'm reaching out regarding our confirmed collaboration on the project "{project_title}" via Servio.

                Everything looks good on my end regarding the agreed deliverables and payment terms, and I'm ready to get started.

                Project Summary:
                - Project: {project_title}
                - Timeline: {timeline}

                Deliverables:
                {deliverables_list}

                Please let me know any initial steps or kickoff requirements you'd like me to follow.

                Looking forward to working together.

                Best regards,  
                {sender_name}

                —
                Sent via Servio by DivGM
                """

        encoded_subject = urllib.parse.quote(subject.strip())
        encoded_body = urllib.parse.quote(body.strip())

        return f"mailto:{recipient.email}?subject={encoded_subject}&body={encoded_body}"