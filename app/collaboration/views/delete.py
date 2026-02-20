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


GigModel = get_registered_model("collaboration", "Gig")
ProposalModel = get_registered_model("collaboration", "Proposal")


class DeleteGigView(LoginRequiredMixin, View):
    allowed_http_methods = ["POST"]

    def post(self, request, *args, **kwargs):
        gig_slug = kwargs.get("slug")
        # slug = kwargs.get("slug")

        try:
            status, message = self.delete_gig(gig_slug)

        except GigModel.DoesNotExist:
            return JsonResponse({
                "error": "Not found",
                "message": "Could not locate gig, check and try again.",
            }, status=404)
            
        except GigError as err:
            return JsonResponse({
                "error": err.error,
                "status": err.type,
                "message": err.message,
                
            }, status=err.status_code)

        except IntegrityError as err:
            return JsonResponse({
                "error": "Gig Conflict",
                "message": str(err),
            }, status=409)

        return JsonResponse({
            "status": status,
            "message": message,
            "redirect": reverse_lazy(CollaborationURLS.LIST_COLLABORATIONS),
        }, status=200)
        
    def delete_gig(self, gig_slug):
        try:
            with transaction.atomic():
                gig = (
                    GigModel.objects
                    .select_for_update()
                    .prefetch_related("required_roles__proposals")
                    .get(slug=gig_slug, creator=self.request.user)
                )
                roles = gig.required_roles.all()
                has_proposals = any(
                    role.proposals.exists()
                    for role in roles
                )

                if gig.status in [GigStatus.DRAFT, GigStatus.PENDING]:
                    if roles:
                        roles.delete()
                        
                    gig.delete()
                    return "deleted", "Gig deleted successfully."

                if gig.status == GigStatus.PUBLISHED and not has_proposals:
                    if roles:
                        roles.delete()
                        
                    gig.delete()
                    return "deleted", "Gig deleted successfully."

                if has_proposals:
                    gig.status = GigStatus.ARCHIVED
                    gig.is_active = False
                    gig.save(update_fields=["status", "is_active"])

                    return "archived", "Gig has proposals and was archived instead."

                raise GigError(
                    message="This gig can no longer be deleted because it has active proposals.",
                    status_code=409,
                    code="gig_has_proposals"
                )
                
        except GigModel.DoesNotExist:
            raise
        
        except IntegrityError as err:
            import traceback
            traceback.print_exc()
            raise IntegrityError("This gig is currently being modified. Try again.")

