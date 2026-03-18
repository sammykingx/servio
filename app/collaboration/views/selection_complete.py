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
        self.is_creator = self.proposal.gig.creator == self.request.user
        
        self.provider = self.proposal.sender
        self.creator = self.proposal.gig.creator
        
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
        
        whatsapp_msg = self.get_whatsapp_message()
        mail_msg_url = self.get_mailto_url()
        
        context["gig_title"] = self.proposal.gig.title
        context["provider"] = self.provider
        context["creator"] = self.creator
        context["wa_msg"] = whatsapp_msg
        context["mail_msg"] = mail_msg_url
        context["phone"] = self.get_tel_url()
        # context["whatsapp_number"] = proposal.sender.phone_number # Example
        # Add your other context fields here...
        
        return context
    
    def get_whatsapp_message(self):
        project_title = self.proposal.gig.title
        
        if self.is_creator:
            # Creator → Provider
            number = self.provider.profile.mobile_num
            message = (
                f"Hi {self.provider.first_name.title()},\n\n"
                f"I'm reaching out regarding our project *\"{project_title}\"* on *Servio*.\n\n"
                "We've aligned on the deliverables and payment structure, and I'm looking forward "
                "to getting started with you.\n\n"
                "Feel free to use this chat for updates, coordination, and any questions along the way.\n\n"
                "_— Sent via *Servio* by DivGM_"
            )
        else:
            # Provider → Creator
            number = self.creator.profile.mobile_num
            message = (
                f"Hi {self.creator.first_name.title()},\n\n"
                f"I'm reaching out regarding our project *\"{project_title}\"* on *Servio*.\n\n"
                "Everything looks good on my end regarding the deliverables and payment terms, "
                "and I'm ready to get started.\n\n"
                "Happy to coordinate here for updates and next steps.\n\n"
                "_— Sent via *Servio* by DivGM_"
            )

        encoded_message = urllib.parse.quote(message)
        return f"https://wa.me/{number}?text={encoded_message}"
    
    def get_mailto_url(self):
        project_title = self.proposal.gig.title
        subject = f"Project Kickoff: {project_title} (via Servio)"
        # sender_name = sender.first_name.title()
        # recipient_name = recipient.first_name.title()
        
        if self.is_creator:
            # creator to provider
            email = self.provider.email
            body = f"""
                Hi {self.provider.first_name.title()},

                I hope you're doing well.

                I'm reaching out to officially kick off our collaboration on the project "{project_title}" via Servio.

                We've aligned on the scope and payment terms for your role, and I'm looking forward to getting started with you.

                Please feel free to use this channel or WhatsApp for coordination, updates, and any clarifications as we move forward.

                Let me know a good time to align on next steps or kickoff.

                Best regards,  
                {self.creator.full_name.title()}

                —
                Sent via Servio by DivGM
                """
        else:
            email = self.creator.email
            body = f"""
            Hi {self.creator.first_name.title()},

            I hope you're doing well.

            I'm reaching out regarding our confirmed collaboration on the project "{project_title}" via Servio.

            Everything looks good on my end regarding the agreed scope and payment terms for my role, and I'm ready to get started.

            Please let me know the next steps or any initial direction you'd like me to follow.

            Happy to coordinate here or via WhatsApp for updates and communication.

            Looking forward to working with you.

            Best regards,  
            {self.provider.full_name.title()}

            —
            Sent via Servio by DivGM
            """

        encoded_subject = urllib.parse.quote(subject.strip())
        encoded_body = urllib.parse.quote(body.strip())

        return f"mailto:{email}?subject={encoded_subject}&body={encoded_body}"
    
    def get_tel_url(self):
        return None