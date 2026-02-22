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

from collaboration.schemas.send_proposal import AppliedRoles, SendProposal
from constants import SERVICE_FEE, DECIMAL_PLACE
from .exceptions import ProposalValidationError
from .status_codes import ValidationFailure
from registry_utils import get_registered_model
from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import List


GigCategory = get_registered_model("collaboration", "GigCategory")

class ProposalValidator:
    """
    Stateless validator for enforcing proposal invariants.
    Ensures that a proposal is logically consistent with a Gig before creation.
    Pydantic handles types/formats.
    """
    
    @classmethod
    def validate(cls, payload: SendProposal, gig):
        """Orchestrates cross-model validation logic."""
        
        cls._validate_taxonomy_integrity(payload.applied_roles, payload.proposal_value)
        cls._validate_deliverables_timeline(payload.deliverables, gig.end_date)

    @classmethod
    def _validate_taxonomy_integrity(cls, applied_roles: List[AppliedRoles], proposal_value:Decimal):
        industry_ids = set()
        niche_ids = set()
        calc_role_value = Decimal("0")
        
        for role in applied_roles:
            industry_ids.add(role.industry_id)
            niche_ids.add(role.niche_id)
            cls._validate_minimum_role_amount(role)
            calc_role_value += role.proposed_amount or role.role_amoount
        
        validated_industry = cls._validate_industry(industry_ids)
        cls._validate_total_proposal_amount(proposal_value, calc_role_value)   
        cls._validate_niche(niche_ids, validated_industry)

    @classmethod
    def _validate_total_proposal_amount(cls, proposal_value:Decimal, calc_role_value:Decimal):
        service_fee = (
            calc_role_value * Decimal(str(SERVICE_FEE))
        ).quantize(Decimal(str(DECIMAL_PLACE)), rounding=ROUND_HALF_UP)
        calc_proposal_value = calc_role_value + service_fee
        if proposal_value != calc_proposal_value:
            message = (
                f"Double-check your numbers! The proposal worth (${proposal_value:,.2f}) "
                f"doesn't quite match the your roles worth (${calc_proposal_value:,.2f}). "
                "Please ensure they balance out before proceeding."
            )
            raise ProposalValidationError(
                message,
                code=ValidationFailure.UNBALANCED_BUDGET.code,
                title=ValidationFailure.UNBALANCED_BUDGET.title
            )
            
    @classmethod
    def _validate_industry(cls, industry_ids: set):
        if len(industry_ids) > 1:
            raise ProposalValidationError(
                "Applying to multiple industries in one proposal is not allowed.",
                code=ValidationFailure.MULTIPLE_INDUSTRIES_NOT_ALLOWED.code,
                title=ValidationFailure.MULTIPLE_INDUSTRIES_NOT_ALLOWED.title
            )
        
        industry_id = next(iter(industry_ids))
        try:
            industry_obj = GigCategory.objects.get(
                id=industry_id, 
                parent__isnull=True, 
                is_active=True
            )
        except GigCategory.DoesNotExist:
            raise ProposalValidationError(
                f"Industry ID {industry_id} is invalid or inactive.",
                code=ValidationFailure.INVALID_INDUSTRY,
                title=ValidationFailure.INVALID_INDUSTRY.title
            )
        
        return industry_obj

    @classmethod
    def _validate_niche(cls, niche_ids: set, validated_industry):
        valid_niche_ids = set(validated_industry.active_subcategories().values_list('id', flat=True))
        invalid_niche_ids = niche_ids - valid_niche_ids
        if invalid_niche_ids:
            raise ProposalValidationError(
                f"Niches {list(invalid_niche_ids)} do not belong to the selected industry.",
                code=ValidationFailure.INVALID_ROLE,
                title=ValidationFailure.INVALID_ROLE.title
            )

    @classmethod
    def _validate_minimum_role_amount(cls, role: AppliedRoles):
        final_amount = role.proposed_amount if role.proposed_amount is not None else role.role_amount
        if final_amount < 50:
            raise ProposalValidationError(
                "Quality work deserves more than pocket change! Please ensure each role amount is at least $50.",
                code=ValidationFailure.INVALID_AMOUNT,
                title=ValidationFailure.INVALID_AMOUNT.title,
            )

    @classmethod
    def _validate_deliverables_timeline(cls, deliverables, gig_end_date):
        if not gig_end_date:
            return

        cutoff_date = gig_end_date - timedelta(days=3)
        for d in deliverables:
            if d.due_date > cutoff_date:
                raise ProposalValidationError(
                    f"Deliverable due date must be on or before {cutoff_date}.",
                    code=ValidationFailure.DURATION_EXCEEDS_LIMIT,
                    title=ValidationFailure.DURATION_EXCEEDS_LIMIT.title
                )