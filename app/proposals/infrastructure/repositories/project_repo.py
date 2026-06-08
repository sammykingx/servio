"""
Project Repository Module

This module is responsible for retrieving and persisting Project (Gig) data
from the database and translating ORM models into domain-level ProjectEntity
objects.

It acts as the anti-corruption layer between the Django ORM and the domain layer,
ensuring that the domain remains persistence-agnostic.

Responsibilities:
- Fetching Project/Gig records from the database
- Enforcing basic query constraints (ownership, status, visibility if needed)
- Converting ORM models into domain entities
"""

from django.db.models import Model, Prefetch
from core.model_registry import registry
from proposals.domain.entities import ProjectEntity, ProjectRoleEntity
from proposals.domain.exceptions import ProposalError
from proposals.domain.status_codes import PolicyFailure
from typing import Union
from uuid import UUID


class ProjectRepository:
    def __init__(self):
        self.model = registry.Gig

    def get_by_pk(self, project_id: UUID, *, with_lock:bool=False, as_entity: bool = True) -> Union[Model, ProjectEntity]:
        """
        Fetches a project by it's primary key with optimized relations, optionally locking the row or bypassing domain conversion.

        Args:
            project_id (UUID): Unique identifier of the project.
            with_lock (bool): If True, applies an exclusive row-level lock (SELECT FOR UPDATE).
            as_entity (bool): If True, converts the Django model instance into a domain entity. 
                Set to False to return the raw ORM object for foreign key assignments.
        """
        queryset = (
            self.model.objects
            .select_related("creator")
            .prefetch_related(
                Prefetch(
                    "required_roles",
                    queryset=registry.GigRole.objects.only(
                        "id",
                        "gig_id",
                        "niche_id",
                        "niche_name",
                        "role_id",
                        "role_name",
                        "description",
                        "budget",
                        "payment_option",
                        "status",
                        "slots",
                    )
                )
            )
        )

        if with_lock:
            project = (
                queryset
                .select_for_update(nowait=True)
                .filter(pk=project_id)
                .first()
            )
        else:
            project = queryset.filter(id=project_id).first()

        if not project:
            raise ProposalError(
                "Invalid referenced project",
                code=PolicyFailure.INVALID_OBJECT.code,
                title=PolicyFailure.INVALID_OBJECT.title
            )

        return self._to_entity(project) if as_entity else project

    # ------------------------------------------------------------
    # INTERNAL MAPPING LAYER
    # ------------------------------------------------------------

    def _to_entity(self, project) -> ProjectEntity:
        """
            Converts a Django ORM project model into a ProjectEntity.
            This acts as the anti-corruption layer separating domain from data.
        """
        project_roles = [
            ProjectRoleEntity(
                id=role.id,
                niche=role.niche_id,
                niche_name=role.niche_name,
                role_id=role.role_id,
                role_name=role.role_name,
                description=role.description,
                budget=role.budget,
                payment_plan=role.payment_option,
                status=role.status,
                slots=role.slots
            )
            for role in project.required_roles.all()
        ] if project.has_gig_roles else []

        return ProjectEntity(
            id=project.id,
            title=project.title,
            slug=project.slug,
            description=project.description,
            visibility=project.visibility,
            total_budget=project.total_budget,
            is_gig_active=project.is_gig_active,
            has_gig_roles=project.has_gig_roles,
            is_negotiable=project.is_negotiable,
            creator=project.creator,
            status=project.status,
            start_date=project.start_date,
            end_date=project.end_date,
            required_roles=project_roles
        )
    
    
__all__ = [ProjectRepository]
