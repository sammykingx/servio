"""
PROPOSAL VALIDATORS
===================

PURPOSE:
Enforces Domain Invariants and Structural Integrity. 
Answers: "Is this specific Proposal data valid in and of itself?"

SCOPE:
- Validates payload state (e.g., non-negative price).
- Checks cross-field invariants (e.g., duration vs. gig limit).
- Pure logic: No side effects, no DB writes, no external API calls.

NON-GOALS:
- Business Policies (e.g., "Has the user reached their monthly limit?").
- Infrastructure (e.g., Schema/Form validation).
- Orchestration (e.g., Sending emails or updating state).
"""
from core.model_registry import registry
from proposals.application.dto.send_proposal import ProposedRole, ProposalSubmissionPayload
from proposals.domain.entities import ProjectEntity
from proposals.domain.status_codes import ValidationFailure
from .exceptions import ProposalValidationError
from .status_codes import ValidationFailure
from decimal import Decimal
from typing import Dict, Set


GigCategory = registry.GigCategory


class ProposalValidator:
    """
    Stateless validator for enforcing proposal invariants.
    Ensures that a proposal is logically consistent with a Gig before creation.
    Pydantic handles types/formats.
    """

    @classmethod
    def validate(cls, payload: ProposalSubmissionPayload, project: ProjectEntity):
        """Orchestrates cross-model validation logic."""

        industry_ids = set()
        applied_role_ids = set()
        calc_role_amount = Decimal("0")
        applied_roles_map:Dict[int, str] = {} # { role_id: role_name }
        payload_taxonmy_map = {} # { industry_id: { niche_ids } }
        
        for role in payload.applied_roles:
            industry_ids.add(role.industry_id)
            applied_role_ids.add(role.niche_id)
            calc_role_amount += role.proposed_amount
            applied_roles_map[role.niche_id] = role.niche_name
            
            if role.industry_id not in payload_taxonmy_map:
                payload_taxonmy_map[role.industry_id] = set()
                
            payload_taxonmy_map[role.industry_id].add(role.niche_id)
            
        if project.has_gig_roles:
            cls._validate_defined_project_roles(
                project, applied_role_ids, applied_roles_map
            )
            
        else:
            cls._validate_open_project_taxonomy(
                payload_taxonmy_map, applied_roles_map
            )
            
        # cls._validate_deliverables_timeline(payload.deliverables, gig.end_date)
    
    @classmethod
    def _validate_defined_project_roles(cls, project: ProjectEntity, applied_role_ids: Set[int], applied_roles_map: Dict[int, str]):
        allowed_role_ids = {role.role_id for role in project.required_roles}
        invalid_roles = applied_role_ids - allowed_role_ids
        if invalid_roles:
            invalid_role_names = [ applied_roles_map[role] for role in invalid_roles]
            raise ProposalValidationError(
                f"The Selected roles {invalid_role_names} are not requested within this project's scope.",
                code=ValidationFailure.INVALID_ROLE.code,
                title=ValidationFailure.INVALID_ROLE.title,
            )
    
    @classmethod
    def _validate_open_project_taxonomy(cls, payload_map: Dict[int, Set[int]], applied_roles_map: Dict[int, str]) -> None:
        """
        Validates open taxonomy by batching subcategory verification per industry.
        Guarantees 1 query per industry instead of querying for every single sub-role.
        """
        for industry_id, applied_niche_ids in payload_map.items():
            valid_subcategories_in_db = (
                GigCategory.objects
                .filter(
                    parent_id=industry_id, 
                    is_active=True, 
                    id__in=applied_niche_ids
                )
                .values_list("id", flat=True)
            )
            
            valid_niche_set = set(valid_subcategories_in_db)
            invalid_niches = applied_niche_ids - valid_niche_set
            
            if not valid_niche_set:
                raise ProposalValidationError(
                    "You selected and unrecognized industry",
                    code=ValidationFailure.INVALID_INDUSTRY.code,
                    title=ValidationFailure.INVALID_INDUSTRY.title
                )
                
            if invalid_niches:
                invalid_role_names = [applied_roles_map[role_id] for role_id in invalid_niches]
                raise ProposalValidationError(
                    f"These roles {invalid_role_names} isn't part of a recognized industry",
                    code=ValidationFailure.INVALID_ROLE.code,
                    title=ValidationFailure.INVALID_ROLE.title
                )
