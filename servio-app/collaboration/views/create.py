from django.apps import apps
from django.http import Http404
from django.db import transaction, IntegrityError, OperationalError
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.http.response import HttpResponse, JsonResponse
from django.db.models import Model, Prefetch
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.utils.safestring import mark_safe
from collaboration.models.choices import GigStatus
from template_map.collaboration import Collabs
from core.url_names import CollaborationURLS
from formatters.pydantic_formatter import format_pydantic_errors
from ..schemas import CreateGigRequest, CreateGigStates, get_response_msg
from ..exceptions import GigError
from ..schemas.gig import GigPayload
from ..schemas.gig_role import WORKMODE_OPTIONS
from pydantic import ValidationError
from typing import Dict, List
import json


GigCategory = apps.get_model("collaboration", "GigCategory")
GigModel = apps.get_model("collaboration", "Gig")
GigRoleModel = apps.get_model("collaboration", "GigRole")
GigApplicationModel = apps.get_model("collaboration", "GigApplication")


def create_taxonomy_context() -> List[Dict[str, str | List]]:
    niches = (
        GigCategory.objects.filter(parent__isnull=True, is_active=True)
        .prefetch_related(
            Prefetch(
                "subcategories",
                queryset=GigCategory.objects.filter(is_active=True).order_by("name"),
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


class CreateCollaborationView(LoginRequiredMixin, View):
    """
    Docstring for CreateCollaborationView
    """

    http_method_names = ["get", "post"]

    def get(self, request) -> HttpResponse:
        context = {
            "gig_taxonomy": create_taxonomy_context(),
            "workmode_labels": json.dumps(WORKMODE_OPTIONS),
        }
        return render(request, Collabs.CREATE, context)

    def post(self, request) -> JsonResponse:
        try:
            payload = json.loads(request.body)
            gig_data = CreateGigRequest(**payload)
            gig = self.save_gig_data(gig_data.payload, gig_data.action)

        except json.JSONDecodeError:
            return JsonResponse(
                {
                    "error": "Invalid JSON payload",
                    "message": "Request body should be a valid JSON data, check and try again.",
                },
                status=400,
            )

        except ValidationError as e:
            return JsonResponse(
                {
                    "error": "Validation error",
                    "message": "Some required information is missing or invalid.",
                    "fields": format_pydantic_errors(e),
                },
                status=400,
            )
        except IntegrityError as err:
            return JsonResponse(
                {
                    "error": "Data Conflict Error",
                    "message": err,
                },
                status=400,
            )

        except OperationalError as err:
            return JsonResponse(
                {
                    "error": "Data Conflict Error",
                    "message": err,
                },
                status=400,
            )

        response = get_response_msg(gig_data.action, gig)
        return JsonResponse(response.model_dump())

    def save_gig_data(self, payload: GigPayload, action: CreateGigStates) -> Model:
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
                    has_gig_roles=True if payload.roles else False,
                    status=(
                        GigStatus.PENDING
                        if action == CreateGigStates.PUBLISH
                        else GigStatus.DRAFT
                    ),
                )

                if payload.roles:
                    niche_ids = {role.nicheId for role in payload.roles}
                    categories = GigCategory.objects.in_bulk(niche_ids)
                    missing_ids = niche_ids - categories.keys()
                    if missing_ids:
                        raise IntegrityError(
                            "One or more selected categories are invalid or no longer available."
                        )
                    
                    aggregated_roles = {}

                    for role in payload.roles:
                        key = (role.nicheId, role.professionalId)

                        if key not in aggregated_roles:
                            aggregated_roles[key] = {
                                "role": role,
                                "slots": role.slots or 1,
                            }
                        else:
                            aggregated_roles[key]["slots"] += role.slots or 1
                        
                    roles = [
                        GigRoleModel(
                        gig=gig,
                        niche=categories[niche_id],
                        niche_name=data["role"].niche,
                        role_name=data["role"].professional,
                        role_id=professional_id,
                        budget=data["role"].budget,
                        workload=data["role"].workload,
                        description=data["role"].description,
                        slots=data["slots"],
                        is_negotiable=payload.isNegotiable,
                    )
                    for (niche_id, professional_id), data in aggregated_roles.items()
                ]

                    GigRoleModel.objects.bulk_create(roles)

        except IntegrityError as e:
            raise IntegrityError(
                "This gig/project could not be saved due to a data conflict. try again shortly."
            )
        except OperationalError as e:
            raise OperationalError(
                "We’re having trouble saving your gig right now. Please try again shortly."
            )

        return gig


class EditGigView(LoginRequiredMixin, View):
    allowed_http_methods = ["GET", "POST"]
    template_name = Collabs.EDIT

    def get_queryset(self):
        return (
            GigModel.objects.filter(creator=self.request.user)
            .select_related("creator")
            .prefetch_related(
                Prefetch(
                    "required_roles",
                    queryset=GigRoleModel.objects.select_related(
                        "niche"
                    ).prefetch_related(
                        Prefetch(
                            "applications",
                            queryset=GigApplicationModel.objects.select_related("user"),
                        )
                    ),
                )
            )
        )

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except Http404:
            return redirect(CollaborationURLS.LIST_COLLABORATIONS)

    def get(self, request, slug) -> HttpResponse:
        try:
            gig = self.get_queryset().get(slug=slug)
            roles = gig.required_roles.all().order_by("-created_at")
            
        except GigModel.DoesNotExist:
            return redirect(CollaborationURLS.LIST_COLLABORATIONS)

        roles_payload = [
            {
                "nicheId": role.niche_id,
                "nicheName": role.niche_name,
                "professionalId": role.role_id,
                "professionalName": role.role_name,
                "budget": float(role.budget),
                "description": role.description,
                "workload": role.workload,
                "slots": role.slots,
            }
            for role in roles
        ]   
        
        for role in roles:
            applicants = role.applications.all()
            
        context = {
            "gig": gig,
            "gig_roles_json": json.dumps(roles_payload),
            "gig_taxonomy": create_taxonomy_context(),
            "workmode_labels": json.dumps(WORKMODE_OPTIONS),
            "editable_statuses": ["pending", "draft"],
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        gig_id = kwargs.get("gig_id")
        try:
            gig = self.get_queryset().get(id=gig_id)
            payload = json.loads(request.body)
            gig_data = GigPayload(**payload)
            self.update_gig_data(gig_id, gig_data)
            
        except GigModel.DoesNotExist:
            return redirect(CollaborationURLS.LIST_COLLABORATIONS)
        
        except json.JSONDecodeError:
            return JsonResponse(
                {
                    "error": "Invalid JSON payload",
                    "message": "Request body should be a valid JSON data, check and try again.",
                },
                status=400,
            )
        
        except ValidationError as e:
            return JsonResponse(
                {
                    "error": "Validation error",
                    "message": "Some required information is missing or invalid.",
                    "fields": format_pydantic_errors(e),
                },
                status=400,
            )
        
        except GigError as err:
            return JsonResponse(
        {
            "error": err.error,
            "message": err.message,
            "status": err.type,
        },
        status=err.status_code,
    )
        return JsonResponse(
            {
                "status": "success",
                "message": "Gig updated successfully.",
                # "url": reverse_lazy(CollaborationURLS.LIST_COLLABORATIONS),
            },
            status=200,
        )
    
    def update_gig_data(self, gig_id, payload: GigPayload) -> Model:
        try:
            with transaction.atomic():
                # ---------------------------------
                # Lock gig row (prevents race edits)
                # ---------------------------------
                gig = (
                    GigModel.objects
                    .select_for_update()
                    .get(id=gig_id, creator=self.request.user)
                )
                
                if gig.status not in (GigStatus.DRAFT, GigStatus.PENDING):
                    raise GigError(
                        message="Live gigs can only be edited using the live update workflow.",
                        status_code=403,
                        code="GIG_EDIT_NOT_ALLOWED"
                    )

                # ---------------------------------
                # Update gig fields
                # ---------------------------------
                gig.title = payload.title
                gig.description = payload.description
                gig.total_budget = payload.projectBudget
                gig.visibility = payload.visibility
                gig.start_date = payload.startDate
                gig.end_date = payload.endDate
                gig.is_negotiable = payload.isNegotiable
                gig.has_gig_roles = True if payload.roles else False

                gig.full_clean()
                gig.save()

                roles_payload = payload.roles or []

                # ---------------------------------
                # If no roles -> delete all roles
                # ---------------------------------
                if not roles_payload:
                    roles_with_applicants = GigRoleModel.objects.filter(gig=gig, applications__isnull=False)
                    if roles_with_applicants.exists():
                        raise IntegrityError(
                            "Cannot remove roles that have active applications."
                        )
                    
                    GigRoleModel.objects.filter(gig=gig).delete()
                    return gig


                # ---------------------------------
                # Resolve & validate categories
                # ---------------------------------
                niche_ids = {role.nicheId for role in roles_payload}
                categories = GigCategory.objects.in_bulk(niche_ids)

                missing_ids = niche_ids - categories.keys()
                if missing_ids:
                    raise IntegrityError(
                        "One or more selected categories are invalid or no longer available."
                    )

                # ---------------------------------
                # Aggregate duplicate roles -> slots
                # ---------------------------------
                aggregated_roles = {}
                new_roles = []
                updated_roles = []

                for role_data in roles_payload:
                    key = (role_data.nicheId, role_data.professionalId)

                    if key not in aggregated_roles:
                        aggregated_roles[key] = {
                            "data": role_data,
                            "slots": role_data.slots or 1,
                        }
                    else:
                        aggregated_roles[key]["slots"] += role_data.slots or 1

                # ---------------------------------
                # Load existing roles
                # ---------------------------------
                existing_roles = {
                    (role.niche_id, role.role_id): role
                    for role in GigRoleModel.objects.filter(gig=gig)
                }

                incoming_keys = set()

                # ---------------------------------
                # Upsert roles
                # ---------------------------------
                for (niche_id, role_id), bundle in aggregated_roles.items():
                    role_data = bundle["data"]
                    slots = bundle["slots"]

                    key = (niche_id, role_id)
                    incoming_keys.add(key)

                    if key in existing_roles:
                        # Update existing role
                        role = existing_roles[key]

                        role.niche = categories[niche_id]
                        role.niche_name = role_data.niche
                        role.role_id = role_id
                        role.role_name = role_data.professional
                        role.budget = role_data.budget
                        role.workload = role_data.workload
                        role.description = role_data.description
                        role.slots = slots

                        updated_roles.append(role)

                    else:
                        # Create new role
                        new_roles.append(
                            GigRoleModel(
                                gig=gig,
                                niche=categories[niche_id],
                                niche_name=role_data.niche,
                                role_id=role_id,
                                role_name=role_data.professional,
                                budget=role_data.budget,
                                workload=role_data.workload,
                                description=role_data.description,
                                slots=slots,
                            )
                        )

                if new_roles:
                    GigRoleModel.objects.bulk_create(new_roles)
                    
                for role in updated_roles:
                    role.full_clean()
                    role.save()
                
                # ---------------------------------
                # Delete removed roles from exisiting roles
                # ---------------------------------
                for key, role in existing_roles.items():
                    if key not in incoming_keys:
                        role.delete()

                return gig

        except ValidationError as e:
            raise IntegrityError(f"Validation failed: {e}")
        
        except IntegrityError:
            raise IntegrityError(
                "This gig/project could not be saved due to a data conflict. Please try again."
            )

        except OperationalError:
            raise OperationalError(
                "We’re having trouble saving your gig right now. Please try again shortly."
            )
