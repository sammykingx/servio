from django.http import Http404
from django.db import transaction, IntegrityError, OperationalError
from django.shortcuts import render, redirect
from django.http.response import HttpResponse, JsonResponse
from django.db.models import Model, Prefetch
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from collaboration.models.choices import GigStatus
from template_map.collaboration import Collabs
from core.url_names import CollaborationURLS
from formatters.pydantic_formatter import format_pydantic_errors
from registry_utils import get_registered_model
from ..schemas import CreateGigRequest, CreateGigStates, get_response_msg
from ..exceptions import GigError
from ..schemas.gig import GigPayload
from ..schemas.gig_role import PAYMENT_OPTIONS
from pydantic import ValidationError
from typing import Dict, List
import json


GigCategory = get_registered_model("collaboration", "GigCategory")
GigModel = get_registered_model("collaboration", "Gig")
GigRoleModel = get_registered_model("collaboration", "GigRole")
ProposalModel = get_registered_model("collaboration", "Proposal")

# not used
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


class EditGigView(LoginRequiredMixin, View):
    """
    Handles editing of an existing Gig/Project owned by the authenticated user.

    This class-based view supports both rendering the gig edit interface (GET)
    and processing gig updates submitted as JSON (POST). Only gigs/projects created by
    the currently authenticated user can be accessed or modified.

    High-level behavior:
    --------------------
    - Restricts access to authenticated users only.
    - Ensures the gig belongs to the requesting user.
    - Allows editing only when the gig is in DRAFT or PENDING status.
    - Performs all updates inside a database transaction to prevent race
      conditions and partial writes.
    - Supports full gig/project updates, including:
        * Core gig/project fields (title, description, dates, budget, visibility)
        * Associated gig/project roles (create, update, aggregate, delete)
    - Prevents destructive changes (e.g., deleting roles) when active
      proposals exist.

    GET request flow:
    -----------------
    - Fetches the gig and its related roles, niches, and proposals using
      optimized querysets.
    - Serializes gig roles into a JSON-compatible payload for frontend usage.
    - Provides taxonomy and payment metadata required by the edit UI.
    - Redirects to the collaboration list if the gig does not exist or is
      inaccessible.

    POST request flow:
    ------------------
    - Expects a JSON payload describing the updated gig state.
    - Validates the payload using a Pydantic schema.
    - Delegates update logic to `update_gig_data`, which performs:
        * Row-level locking
        * Validation
        * Role aggregation and upsert logic
    - Returns structured JSON responses for success and all error cases.

    Error handling:
    ---------------
    - Gracefully redirects on missing gigs or permission issues.
    - Returns JSON error responses for:
        * Invalid JSON payloads
        * Validation failures
        * Business-rule violations
        * Database integrity or operational errors

    This view is designed to be safe, transactional, and frontend-friendly,
    making it suitable for asynchronous editing workflows.
    """
    allowed_http_methods = ["GET", "POST"]
    template_name = Collabs.EDIT

    def get_queryset(self):
        """
        Returns a queryset of gigs owned by the current user with all required
        related data eagerly loaded.

        Optimizations:
        - Selects the gig creator using `select_related`
        - Prefetches required roles
        - Prefetches role proposals and their associated users

        This queryset is used consistently across GET and POST requests to enforce
        ownership and reduce database queries.
        """
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
                            "proposals",
                            queryset=ProposalModel.objects.select_related("user"),
                        )
                    ),
                )
            )
        )

    def dispatch(self, request, *args, **kwargs):
        """
        Wraps the standard dispatch method to gracefully handle 404 errors.

        If a Http404 is raised during request processing (e.g., gig not found),
        the user is redirected to the collaborations list instead of seeing
        a default error page.
        """
        try:
            return super().dispatch(request, *args, **kwargs)
        except Http404:
            return redirect(CollaborationURLS.LIST_COLLABORATIONS)

    def get(self, request, slug) -> HttpResponse:
        """
        Renders the gig edit page.

        Fetches the specified gig and its associated roles, then prepares a
        serialized JSON payload consumed by the frontend editing interface.

        Context includes:
        - The gig instance
        - Serialized gig roles
        - Taxonomy metadata
        - Payment option labels
        - Editable gig statuses

        Redirects to the collaboration list if the gig does not exist or does
        not belong to the current user.
        """
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
                "workload": role.payment_option,
                "slots": role.slots,
            }
            for role in roles
        ]   
        
        for role in roles:
            applicants = role.proposals.all()
            
        context = {
            "gig": gig,
            "gig_roles_json": json.dumps(roles_payload),
            "gig_taxonomy":  GigCategory.objects.get_taxonomy_json(),
            "payment_labels": json.dumps(PAYMENT_OPTIONS),
            "editable_statuses": ["pending", "draft"],
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        """
        Processes updates to an existing gig.

        Expects a JSON request body matching the `GigPayload` schema. The payload
        is validated and then passed to `update_gig_data` for transactional
        persistence.

        Returns:
        - 200 JSON response on successful update
        - 400 for invalid JSON or validation errors
        - Custom error responses for business-rule violations
        - Redirects if the gig does not exist or is inaccessible
        """
        gig_slug = kwargs.get("slug")
        try:
            gig = self.get_queryset().get(slug=gig_slug)
            payload = json.loads(request.body)
            gig_data = GigPayload(**payload)
            self.update_gig_data(gig_slug, gig_data)
            
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
    
    def update_gig_data(self, gig_slug, payload: GigPayload) -> Model:
        """
            Applies validated gig updates inside a database transaction.

            Responsibilities:
            -----------------
            - Locks the gig row using `select_for_update` to prevent concurrent edits
            - Verifies the gig is editable based on its current status
            - Updates core gig fields
            - Handles role synchronization:
                * Aggregates duplicate roles into slot counts
                * Creates new roles
                * Updates existing roles
                * Deletes removed roles when safe
            - Prevents deletion of roles with active proposals
            - Ensures all category references are valid

            All changes are atomic: if any step fails, the transaction is rolled back.

            Raises:
            -------
            - IntegrityError for data conflicts or invalid operations
            - OperationalError for database-level failures

            Returns:
            --------
            The updated Gig instance on success.
        """
        try:
            with transaction.atomic():
                # ---------------------------------
                # Lock gig row (prevents race edits)
                # ---------------------------------
                gig = (
                    GigModel.objects
                    .select_for_update()
                    .get(slug=gig_slug, creator=self.request.user)
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
                    roles_with_applicants = GigRoleModel.objects.filter(gig=gig, proposals__isnull=False)
                    if roles_with_applicants.exists():
                        raise IntegrityError(
                            "Cannot remove roles that have active proposals."
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
                        role.payment_option = role_data.paymentOption
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
