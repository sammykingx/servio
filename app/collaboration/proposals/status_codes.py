"""
Proposal-related error codes for domain exceptions.
These codes can be used across policies, validators, and services.
"""

from typing import NamedTuple, Optional


class FailureDetail(NamedTuple):
    code: str
    title: str

# -----------------------------
# Permission / Policy Codes
# -----------------------------
class PolicyFailure:
    # Format: FailureDetail(CODE, HUMAN_READABLE_TITLE)
    CANNOT_APPLY_TO_OWN_GIG = FailureDetail("CANNOT_APPLY_TO_OWN_GIG", "Self-Application Restricted")
    GIG_NOT_PUBLISHED = FailureDetail("GIG_NOT_PUBLISHED", "Project Unavailable")
    GIG_START_DATE_PASSED = FailureDetail("GIG_START_DATE_PASSED", "Application Window Closed")
    GIG_ALREADY_STARTED = FailureDetail("GIG_ALREADY_STARTED", "Project In Progress")
    NOT_QUALIFIED_FOR_ROLES = FailureDetail("NOT_QUALIFIED_FOR_ROLES", "Requirement Mismatch")
    
    SUBSCRIPTION_REQUIRED = FailureDetail("SUBSCRIPTION_REQUIRED", "Subscription Required")
    PAYMENT_PENDING = FailureDetail("PAYMENT_PENDING", "Pending Payment")
    
    APPLICATION_RESTRICTED = FailureDetail("APPLICATION_RESTRICTED", "Access Denied")
    DUPLICATE_APPLICATION = FailureDetail("DUPLICATE_APPLICATION", "Already Applied")


# -----------------------------
# Validation / Domain Codes
# -----------------------------
class ValidationFailure:
    INVALID_AMOUNT = FailureDetail("INVALID_AMOUNT", "Fair Pricing Policy")
    DURATION_EXCEEDS_LIMIT = FailureDetail("DURATION_EXCEEDS_LIMIT", "Duration Too Long")
    INVALID_INDUSTRY = FailureDetail("INVALID_INDUSTRY", "Invalid Industry Selected")
    MULTIPLE_INDUSTRIES_NOT_ALLOWED = FailureDetail("MULTIPLE_INDUSTRIES_NOT_ALLOWED", "Single Industry Required")
    INVALID_ROLE = FailureDetail("INVALID_ROLE", "Invalid Role Selected")
