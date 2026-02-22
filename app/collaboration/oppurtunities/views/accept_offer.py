from django.http import Http404, JsonResponse
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from collaboration.models.choices import GigStatus, PaymentOption
from collaboration.proposals.exceptions import ProposalError
from collaboration.proposals.services import ProposalService
from collaboration.schemas.gig_role import PAYMENT_OPTIONS
from collaboration.schemas.send_proposal import SendProposal
from core.url_names import OppurtunitiesURLS
from template_map.collaboration import Collabs
from registry_utils import get_registered_model
from pydantic import ValidationError
import json


GigCategoryModel = get_registered_model("collaboration", "GigCategory")
GigModel = get_registered_model("collaboration","Gig")
GigRoleModel = get_registered_model("collaboration", "GigRole")


class AcceptOppurtuniyDetailView(LoginRequiredMixin, DetailView):
    model = GigModel
    template_name = Collabs.Oppurtunities.ACCEPT_OFFER
    context_object_name = "gig"
    slug_field = "slug"
    slug_url_kwarg = "slug"
    
    def get_queryset(self):
        return super().get_queryset().filter(
            status=GigStatus.PUBLISHED
        ).exclude(creator=self.request.user)
    
    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except Http404:
            return redirect(reverse_lazy(OppurtunitiesURLS.ALL))
    
    def get_context_data(self, **kwargs):
        context =super().get_context_data(**kwargs)
        context["taxonomy_json"] = GigCategoryModel.objects.get_taxonomy_json()
        context["payment_options"] = json.dumps(PAYMENT_OPTIONS)
        context["negotiating"] = True if self.request.GET.get("negotiating") == "true" else False
        roles = self.object.required_roles.all()
        role_payment_plan = {}
        if roles:
            for role in roles:
                role.can_apply = user_can_apply_for_role(self.request.user, role)
                payment_value = role.payment_option

                is_split = PaymentOption.is_split(payment_value)

                role_payment_plan[role.id] = {
                    "type": "Percentage Split" if is_split else "Full Upfront",
                    "installments": (
                        PaymentOption.installments_count(payment_value)
                        if is_split
                        else 1
                    ),
                    "split": (
                        PaymentOption.percentages(payment_value)
                        if is_split
                        else [100]
                    ),
                    "label": PaymentOption(payment_value).label,
                }
                
            context["roles"] = roles
            context["role_payment_plan"] = role_payment_plan
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            payload = json.loads(request.body)
            data = SendProposal(**payload)
            ProposalService(request.user).send_proposal(self.object, data)
            
        except json.JSONDecodeError:
            return JsonResponse(
                {
                    "error": "Invalid JSON payload",
                    "message": "Request body should be a valid JSON data, check and try again.",
                },
                status=400,
            )
            
        except ValidationError as err:                
            return JsonResponse(
                {
                    "error": "Validation error",
                    "message": "Some required information is missing or invalid.",
                },
                status=400,
            )
            
        except ProposalError as e:
            return JsonResponse({
                "error": e.title,
                "message": e.message,
                "code": e.code,
                "url": e.redirect_url
                
            }, status=400)
 
        return JsonResponse({
            "title": "Proposal Sent!",
            "status": "success",
            "message": "High five! Your proposal is officially on its way to the creator for review. We'll let you know as soon as they take a look."
        })
    

def user_can_apply_for_role(user, role) -> bool:
    if not user.is_authenticated:
        return False

    user_niches = set(user.profile.get_user_niches)
    return role.role_id in user_niches
