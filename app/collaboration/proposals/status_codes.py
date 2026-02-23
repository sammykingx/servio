"""
Proposal Error Codes Module.
============================

This module defines a centralized registry of domain-specific error codes and 
human-readable titles for failures occurring during the proposal lifecycle. 
These constants are designed to be consumed by policies, validators, and 
application services to ensure consistency in error reporting across the platform.

The module utilizes a `NamedTuple` structure to provide immutable, type-hinted 
failure details that can be easily serialized for API responses or logged 
for debugging purposes.
"""

from typing import NamedTuple, Optional


class FailureDetail(NamedTuple):
    """
    A structured representation of a domain failure.

    Attributes:
        code (str): A unique, machine-readable string identifier (e.g., 'INVALID_AMOUNT').
        title (str): A brief, human-readable description intended for end-user display.
    """
    code: str
    title: str
   

# -----------------------------
# Permission / Policy Codes
# -----------------------------
class PolicyFailure:
    """
    Constants representing authorization and business policy violations.

    These codes are triggered when a user or action violates the fundamental 
    rules of the marketplace, such as eligibility requirements, project status 
    constraints, or subscription-level permissions.
    """
    # Format: FailureDetail(CODE, HUMAN_READABLE_TITLE)
    CANNOT_APPLY_TO_OWN_GIG = FailureDetail("CANNOT_APPLY_TO_OWN_GIG", "Self-Application Restricted")
    EMAIL_NOT_VERIFIED = FailureDetail("EMAIL_VERIFICATION_REQUIRED", "Email Verification Pending")
    GIG_NOT_PUBLISHED = FailureDetail("GIG_NOT_PUBLISHED", "Project Unavailable")
    GIG_START_DATE_PASSED = FailureDetail("GIG_START_DATE_PASSED", "Application Window Closed")
    GIG_ALREADY_STARTED = FailureDetail("GIG_ALREADY_STARTED", "Project In Progress")
    INVALID_ROLE = FailureDetail("INVALID_ROLE", "Role Not Found")
    NOT_QUALIFIED_FOR_ROLES = FailureDetail("NOT_QUALIFIED_FOR_ROLES", "Requirement Mismatch")
    
    SUBSCRIPTION_REQUIRED = FailureDetail("SUBSCRIPTION_REQUIRED", "Subscription Required")
    PAYMENT_PENDING = FailureDetail("PAYMENT_PENDING", "Pending Payment")
    
    APPLICATION_RESTRICTED = FailureDetail("APPLICATION_RESTRICTED", "Access Denied")
    DUPLICATE_APPLICATION = FailureDetail("DUPLICATE_APPLICATION", "Proposal Already in Review")


# -----------------------------
# Validation / Domain Codes
# -----------------------------
class ValidationFailure:
    """
    Constants representing data integrity and business logic validation errors.

    These codes are triggered during the proposal submission process when 
    the provided data (e.g., bid amount, dates, or metadata) fails to meet 
    the technical or logical requirements of the domain.
    """
    INVALID_AMOUNT = FailureDetail("INVALID_AMOUNT", "Fair Pricing Policy")
    UNBALANCED_BUDGET = FailureDetail("UNBALANCED_BUDGET", "Budget Allocation Error")
    DURATION_EXCEEDS_LIMIT = FailureDetail("DURATION_EXCEEDS_LIMIT", "Duration Too Long")
    INVALID_INDUSTRY = FailureDetail("INVALID_INDUSTRY", "Invalid Industry Selected")
    MULTIPLE_INDUSTRIES_NOT_ALLOWED = FailureDetail("MULTIPLE_INDUSTRIES_NOT_ALLOWED", "Single Industry Required")
    INVALID_ROLE = FailureDetail("INVALID_ROLE", "Invalid Role Selected")
