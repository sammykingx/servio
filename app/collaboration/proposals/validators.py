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

from .exceptions import ProposalValidationError

class ProposalValidator:
    """
    Stateless validator for enforcing proposal invariants.
    """
    
    @staticmethod
    def validate(payload, gig):
        """
        Ensures the proposal payload is logically consistent with the target Gig.
        """
        if payload.price <= 0:
            raise ProposalValidationError("Price must be a positive value.")

        if payload.duration > gig.max_duration:
            raise ProposalValidationError("Proposal duration exceeds the maximum allowed for this gig.")