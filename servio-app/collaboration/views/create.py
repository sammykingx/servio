from django.apps import apps
from django.db import transaction, IntegrityError, OperationalError
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.http.response import HttpResponse, JsonResponse
from django.db.models import Prefetch
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import View
from django.utils.safestring import mark_safe
from template_map.collaboration import Collabs
from core.url_names import CollaborationURLS
from ..schemas import CreateGigRequest, CreateGigStates,  get_response_msg
from ..schemas.gig import GigPayload
from ..schemas.gig_role import WORKMODE_OPTIONS
from pydantic import ValidationError
from typing import Dict, List
import json


GigCategory = apps.get_model("collaboration", "GigCategory")


class CreateCollaborationView(LoginRequiredMixin, View):
    """
    Docstring for CreateCollaborationView
    """
    http_method_names = ["get", "post"]
    
            
    def create_taxonomy_context(self) -> List[Dict[str, str|List]]:
        niches = (
            GigCategory.objects
            .filter(parent__isnull=True, is_active=True)
            .prefetch_related(
                Prefetch(
                    "subcategories",
                    queryset=GigCategory.objects.filter(is_active=True).order_by("name")
                )
            )
            .order_by("name")
        )

        taxonomy = [
            {
                "id": niche.id,
                "name": niche.name,
                "subcategories": [
                    {
                        "id": sub.id,
                        "name": sub.name,
                    }
                    for sub in niche.subcategories.all()
                ],
            }
            for niche in niches
        ]

        return json.dumps(taxonomy)

    def get(self, request) -> HttpResponse:
        context = { 
                   "gig_taxonomy" : self.create_taxonomy_context(),
                   "workmode_labels": json.dumps(WORKMODE_OPTIONS),
                }
        return render(request, Collabs.CREATE, context)
    
    def post(self, request) -> JsonResponse:
        try:
            payload = json.loads(request.body)
            gig_data = CreateGigRequest(**payload)
            self.save_gig_data(gig_data.payload, gig_data.action)

        except json.JSONDecodeError:
            return JsonResponse(
                {
                    "error": "Invalid JSON payload",
                    "message": "Request body should be a valid JSON data, check and try again.",
                },
                status=400
            )
            
        except ValidationError as e:
            from formatters.pydantic_formatter import format_pydantic_errors
            return JsonResponse(
                {
                    "error": "Validation error",
                    "message": "Some required information is missing or invalid.",
                    "fields": format_pydantic_errors(e),
                },
                status=400
            )
        except IntegrityError as err:
            return JsonResponse(
                {
                    "error": "Data Conflict Error",
                    "message": err,
                    "fields": format_pydantic_errors(e),
                },
                status=400
            )
            
        except OperationalError as err:
            return JsonResponse(
                {
                    "error": "Data Conflict Error",
                    "message": err,
                    "fields": format_pydantic_errors(e),
                },
                status=400
            )
        
        response = get_response_msg(gig_data.action)
        return JsonResponse(response.model_dump())
    
    def save_gig_data(self, payload:GigPayload, action:CreateGigStates) -> None:
        from collaboration.models.choices import GigStatus
        
        GigModel = apps.get_model("collaboration","Gig")
        GigRoleModel = apps.get_model("collaboration", "GigRole")
        
        try:
            with transaction.atomic():
                gig = GigModel.objects.create(
                    creator=self.request.user,
                    title=payload.title,
                    visibility=payload.visibility,
                    description=payload.description,
                    total_budget=payload.projectBudget,
                    start_date=payload.startDate,
                    end_date=payload.endDate,
                    is_negotiable=payload.isNegotiable,
                    has_gig_roles = True if payload.roles else False,
                    status=GigStatus.PENDING if action == CreateGigStates.PUBLISH else GigStatus.DRAFT,
                )

                if payload.roles:
                    niche_ids = {role.nicheId for role in payload.roles}
                    categories = GigCategory.objects.in_bulk(niche_ids)
                    missing_ids = niche_ids - categories.keys()
                    if missing_ids:
                        raise IntegrityError(
                            "One or more selected categories are invalid or no longer available."
                        )
                    roles = [
                        GigRoleModel(
                            gig=gig,
                            niche=categories[role.nicheId],
                            niche_name=role.niche,
                            role_name=role.professional,
                            role_id=role.professionalId,
                            budget=role.budget,
                            workload=role.workload,
                            description=role.description,
                            is_negotiable=payload.isNegotiable,
                        )
                        for role in payload.roles
                    ]

                    GigRoleModel.objects.bulk_create(roles)

        except IntegrityError as e:
            raise IntegrityError("This gig/project could not be saved due to a data conflict. try again shortly.")
        except OperationalError as e:
            raise OperationalError("We’re having trouble saving your gig right now. Please try again shortly.")

