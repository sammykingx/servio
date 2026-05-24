from django.db import models



class DurationUnit(models.TextChoices):
    DAYS = "days", "Days"
    WEEKS = "weeks", "Weeks"
    MONTHS = "months", "Months"


class ProposalStatus(models.TextChoices):
    # Initial Stages (what providers see)
    SENT = "sent", "Sent"
    
    # # Active Discussion (not implemented)
    # NEGOTIATING = "negotiating", "Negotiation"
      
    # Final Outcomes
    REVIEWED = "reviewed", "Reviewed" # Some roles are "Accepted/Rejected", but some are still "Pending"
    ACCEPTED = "accepted", "Accepted"
    REJECTED = "rejected", "Rejected"
    WITHDRAWN = "withdrawn", "Withdrawn" # providers can withdraw their proposal
    
    
class ProposalRoleStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    ACCEPTED = "accepted", "Accepted"
    REJECTED = "rejected", "Rejected"
    WITHDRAWN = "withdrawn", "Withdrawn"
    