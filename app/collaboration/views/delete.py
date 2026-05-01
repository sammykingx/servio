from django.apps import apps
from django.urls import reverse_lazy
from django.views.generic import View
from django.http.response import JsonResponse
from django.db import transaction, IntegrityError
from django.contrib.auth.mixins import LoginRequiredMixin
from core.url_names import CollaborationURLS
from template_map.collaboration import Collabs
from collaboration.models.choices import GigStatus
from registry_utils import get_registered_model
from ..exceptions import GigError



class DeleteGigView(LoginRequiredMixin, View):
    allowed_http_methods = ["POST"]
    model = get_registered_model("collaboration", "Gig")
    proposal_model = get_registered_model("collaboration", "Proposal")

    def post(self, request, *args, **kwargs):
        gig_slug = kwargs.get("slug")
        try:
            self.delete_gig(gig_slug)
            return JsonResponse({
                "status": "success",
                "message": "Project has been deleted successfully.",
                "redirect": reverse_lazy(CollaborationURLS.LIST_COLLABORATIONS),
            }, status=200)

        except self.model.DoesNotExist:
            return JsonResponse({
                "error": "Not found",
                "message": "Could not locate project, check and try again.",
            }, status=404)
            
        except GigError as err:
            return JsonResponse({
                "error": err.error,
                "status": err.type,
                "message": err.message,
                
            }, status=err.status_code)

        except IntegrityError as err:
            return JsonResponse({
                "error": "Project Conflict",
                "message": str(err),
            }, status=409)
        
    def delete_gig(self, gig_slug, soft_delete=True):
        try:
            with transaction.atomic():
                gig = (
                    self.model.objects
                    .select_for_update()
                    .prefetch_related("required_roles", "proposals")
                    .get(slug=gig_slug, creator=self.request.user)
                )
                
                has_proposals = gig.proposals.exists()
                if has_proposals:
                    raise GigError(
                        message="This project has active proposals and cannot be deleted in its current state.",
                        status_code=409,
                        code="GIG_DELETE_RESTRICTED"
                    )
                
                if not soft_delete:
                    self._handle_hard_delete(gig, has_proposals=has_proposals)
                    
                self._handle_soft_delete(gig)   
                
        except IntegrityError:
            import traceback
            traceback.print_exc()
            raise IntegrityError("This project is currently being modified. Try again.")

    def _handle_soft_delete(self, gig):
        """
        Marks the gig as archived without deleting records.
        Preserves data integrity and allows for potential restoration.
        """
        if gig.status == GigStatus.ARCHIVED:
            return
        
        gig.status = GigStatus.ARCHIVED
        gig.is_gig_active = False
        gig.save(update_fields=["status", "is_gig_active"])
        
    def _handle_hard_delete(self, gig, has_proposals=False):
        """
        Performs a permanent deletion of the gig and its dependencies.
        Only executes if no proposals have been submitted.
        """
                    
        can_hard_delete = (
            gig.status in {GigStatus.DRAFT, GigStatus.PENDING} or 
            (gig.status == GigStatus.PUBLISHED and not has_proposals)
        )
        
        if not has_proposals and can_hard_delete:
            if gig.has_gig_roles:
                gig.required_roles.all().delete()
                
            gig.delete()
            return
