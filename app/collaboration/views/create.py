from django.db import transaction, IntegrityError, OperationalError
from django.shortcuts import render
from django.http.response import HttpResponse, JsonResponse
from django.db.models import Model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from collaboration.models.choices import GigStatus
from template_map.collaboration import Collabs
from formatters.pydantic_formatter import format_pydantic_errors
from registry_utils import get_registered_model
from ..schemas import CreateGigRequest, CreateGigStates, get_response_msg
from ..schemas.gig import GigPayload
from ..schemas.gig_role import PAYMENT_OPTIONS
from pydantic import ValidationError
import json


GigCategory = get_registered_model("collaboration", "GigCategory")
GigModel = get_registered_model("collaboration", "Gig")
GigRoleModel = get_registered_model("collaboration", "GigRole")


class CreateCollaborationView(LoginRequiredMixin, View):
    """
    Handles the creation of collaboration gigs/projects.

    This view supports rendering the collaboration creation page and
    processing gig creation requests submitted via JSON payloads.

    Responsibilities:
    - Renders the gig creation form with required taxonomy and payment data.
    - Accepts and validates JSON payloads for creating gigs.
    - Persists gig and associated role data atomically.
    - Handles draft and publish workflows based on the requested action.
    - Returns structured JSON responses for success and error cases.

    Access is restricted to authenticated users.
    """

    http_method_names = ["get", "post"]

    def get(self, request) -> HttpResponse:
        """
        Render the collaboration creation page.

        Provides the frontend with taxonomy data and available payment
        options required to construct the gig creation form.

        Returns:
            HttpResponse: Rendered HTML page for creating a collaboration.
        """
        context = {
            "gig_taxonomy": GigCategory.objects.get_taxonomy_json(),
            "payment_options": json.dumps(PAYMENT_OPTIONS),
        }
        return render(request, Collabs.CREATE, context)

    def post(self, request) -> JsonResponse:
        """
        Handle gig creation requests submitted as JSON.

        Expects a JSON payload describing the gig details, roles, and
        requested action (e.g., draft or publish). The payload is validated
        using a Pydantic schema before being persisted.

        Error Handling:
        - Returns 400 for invalid JSON payloads.
        - Returns 400 for validation errors or missing required fields.
        - Returns 400 for database integrity or operational errors.

        Returns:
            JsonResponse: A structured response describing the outcome
            of the gig creation process.
        """
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
            fields = format_pydantic_errors(e),
            return JsonResponse(
                {
                    "error": "Validation error",
                    "message": "Some required information is missing or invalid.",
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
        """
            Persist gig and associated role data atomically.

            Creates a Gig record and, if provided, aggregates and creates
            related GigRole records. All database operations are wrapped in
            a transaction to ensure consistency.

            Role entries with the same niche and professional are aggregated
            by summing their slot counts before persistence.

            Args:
                payload (GigPayload): Validated gig and role data.
                action (CreateGigStates): Determines whether the gig is saved
                    as a draft or submitted for publishing.

            Raises:
                IntegrityError: If invalid categories are selected or a data
                    conflict occurs during persistence.
                OperationalError: If a database-level error prevents saving.

            Returns:
                Model: The created Gig instance.
        """
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
                        GigStatus.PUBLISHED
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
                            payment_option=data["role"].paymentOption,
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
