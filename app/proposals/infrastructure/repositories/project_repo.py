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


from core.model_registry import registry
from proposals.domain.entities import ProjectEntity, ProjectRoleEntity
from proposals.domain.exceptions import ProposalPersistenceError
from proposals.domain.status_codes import PolicyFailure
from typing import Optional
from uuid import UUID


class ProjectRepository:
    def __init__(self):
        self.model = registry.Gig
        
        
    def get_by_id(self, project_id: UUID, with_lock:bool=False) -> Optional[ProjectEntity]:
        """
        Retrieves a single project by its unique identifier.

        Args:
            project_id (UUID): Unique identifier of the project.

        Returns:
            ProjectEntity | None:
                A domain entity representing the project if found,
                otherwise None.
        """
        try:
            queryset = (
                self.model.objects
                .select_related("creator")
                .filter(id=project_id)
                .prefetch_related("required_roles") 
            )
            if with_lock:
                project = queryset.select_for_update(nowait=True).first
            else:
                project = queryset.first()
                
        except self.model.DoesNotExist:
            raise ProposalPersistenceError(
                "Invalid referenced project",
                code=PolicyFailure.INVALID_OBJECT.code,
                title=PolicyFailure.INVALID_OBJECT.title
            )

        return self._to_entity(project)
    

    def get_by_slug(self, slug: str) -> Optional[ProjectEntity]:
        """
        Retrieves a project by its slug.

        Args:
            slug (str): Human-readable unique identifier of the project.

        Returns:
            ProjectEntity | None: Domain representation of the project.
        """
        try:
            project = (
                self.model.objects
                .select_related("creator")
                .get(slug=slug)
            )
        except self.model.DoesNotExist:
            raise ProposalPersistenceError(
                "Invalid referenced project",
                code=PolicyFailure.INVALID_OBJECT.code,
                title=PolicyFailure.INVALID_OBJECT.title
            )

        return self._to_entity(project)


    # ------------------------------------------------------------
    # INTERNAL MAPPING LAYER
    # ------------------------------------------------------------

    def _to_entity(self, project) -> ProjectEntity:
        """
        Converts a Django ORM project model into a ProjectEntity.

        This is the anti-corruption layer that ensures the domain layer
        never depends on ORM structures.

        Args:
            project (Gig): Django ORM instance.

        Returns:
            ProjectEntity: Pure domain representation of the project.
        """
        project_roles = [
            {
                ProjectRoleEntity(
                    id=role.id,
                    niche=role.niche,
                    niche_name=role.niche_name,
                    role_id=role.role_role_id,
                    role_name=role.role_name,
                    description=role.description,
                    budget=role.budget,
                    payment_plan=role.payment_option,
                    status=role.status,
                    slots=role.slots
                )
            }
            for role in project.required_roles.all()
        ]
        
        return ProjectEntity(
            id=project.id,
            title=project.title,
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
