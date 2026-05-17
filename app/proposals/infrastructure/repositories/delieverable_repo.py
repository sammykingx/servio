from core.model_registry import registry
from django.contrib.auth.models import AbstractUser
from django.db.models import Model
from proposals.application.dto.send_proposal import ProposalDeliverable
from typing import List


class ProjectDeliverablesRepository:
    
    def __init__(self):
        self.model = registry.ProposalDeliverable
    
    def bulk_create_from_payload(
        self, 
        saved_role: Model, 
        provider: AbstractUser, 
        deliverables_payload: List[ProposalDeliverable]
    ) -> List[any]:
        """
        Translates domain payload objects into Django infrastructure models
        and bulk inserts them in a single query transaction.
        """
        # Formulate pure, un-saved Django ORM model instances
        model_instances = [
            self.model(
                proposal_role=saved_role,
                provider=provider,
                phase=deliv_data.phase,
                description=deliv_data.description,
                duration_unit=deliv_data.duration_unit,
                duration_value=deliv_data.duration_value,
                release_percentage=deliv_data.release_percentage,
                rendering_order=deliv_data.rendering_order
            )
            for deliv_data in deliverables_payload
        ]
        
        if model_instances:
            return self.model.objects.bulk_create(model_instances)
        
        return []