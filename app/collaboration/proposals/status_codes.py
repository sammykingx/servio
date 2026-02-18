"""
Proposal-related error codes for domain exceptions.
These codes can be used across policies, validators, and services.
"""

# -----------------------------
# Permission / Policy Codes
# -----------------------------
class PolicyFailure:
    CANNOT_APPLY_TO_OWN_GIG = "CANNOT_APPLY_TO_OWN_GIG"
    GIG_NOT_PUBLISHED = "GIG_NOT_PUBLISHED"
    GIG_ALREADY_STARTED = "GIG_ALREADY_STARTED"
    NOT_QUALIFIED_FOR_ROLES = "NOT_QUALIFIED_FOR_ROLES"
    SUBSCRIPTION_REQUIRED = "SUBSCRIPTION_REQUIRED"
    PAYMENT_PENDING = "PAYMENT_PENDING"
    APPLICATION_RESTRICTED = "APPLICATION_RESTRICTED"


# -----------------------------
# Validation / Domain Codes
# -----------------------------
class ValidationFailure:
    INVALID_AMOUNT = "INVALID_AMOUNT"
    DURATION_EXCEEDS_LIMIT = "DURATION_EXCEEDS_LIMIT"
    INVALID_DUE_DATE = "INVALID_DUE_DATE"
    DUPLICATE_APPLICATION = "DUPLICATE_APPLICATION"
    INVALID_ROLE = "INVALID_ROLE"
    INVALID_PAYMENT_PLAN = "INVALID_PAYMENT_PLAN"
