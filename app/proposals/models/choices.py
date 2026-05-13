from django.db import models



class DurationUnit(models.TextChoices):
    DAYS = "days", "Days"
    WEEKS = "weeks", "Weeks"
    MONTHS = "months", "Months"


class ProposalStatus(models.TextChoices):
    # Initial Stages (what providers see)
    SENT = "sent", "Sent"
    
    # Engagement Tracking
    REVIEWING = "reviewing", "In Review" # when the cretor opens the proposal to see deliverables, not done yet
    
    # Active Discussion (not implemented)
    NEGOTIATING = "negotiating", "Negotiation"
      
    # Final Outcomes
    ACCEPTED = "accepted", "Accepted"
    REJECTED = "rejected", "Rejected"
    WITHDRAWN = "withdrawn", "Withdrawn" # providers can withdraw their proposal
    
    
class ProposalRoleStatus(models.TextChoices):
    SUBMITTED = "submitted", "Submitted"
    ACCEPTED = "accepted", "Accepted"
    REJECTED = "rejected", "Rejected"
    WITHDRAWN = "withdrawn", "Withdrawn"
    