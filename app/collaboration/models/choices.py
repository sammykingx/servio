from django.db import models


class GigVisibility(models.TextChoices):
    PUBLIC = "public", "Public"
    PRIVATE = "private", "Private"

class GigStatus(models.TextChoices):
    ARCHIVED = "archived", "Archived"
    DRAFT = "draft", "Draft"
    PENDING = "pending", "Pending"
    PUBLISHED = "published", "Published"
    IN_PROGRESS = "in_progress", "In Progress"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"

class PaymentOption(models.TextChoices):
    FULL_UPFRONT = "full_upfront", "Full Upfront"
    
    SPLIT_50_50 = "split_50_50", "Split 50% / 50%"
    SPLIT_60_40 = "split_60_40", "Split 60% / 40%"
    SPLIT_70_30 = "split_70_30", "Split 70% / 30%"
    
    SPLIT_30_40_30 = "split_30_40_30", "Split 30% / 40% / 30%"
    SPLIT_40_30_30 = "split_40_30_30", "Split 40% / 30% / 30%"
    SPLIT_50_30_20 = "split_50_30_20", "Split 50% / 30% / 20%"
    
    @classmethod
    def is_split(cls, value):
        return value.startswith("split_")

    @classmethod
    def percentages(cls, value) -> list[int]:
        parts = value.replace("split_", "").split("_")
        return [int(p) for p in parts]

    @classmethod
    def installments_count(cls, value) -> int:
        return len(cls.percentages(value))
    
    @property
    def label(self) -> str:
        return {
            self.FULL_UPFRONT: "100% Upfront",
            self.SPLIT_50_50: "50% / 50%",
            self.SPLIT_60_40: "60% / 40%",
            self.SPLIT_70_30: "70% / 30%",
            self.SPLIT_30_40_30: "30% / 40% / 30%",
            self.SPLIT_40_30_30: "40% / 30% / 30%",
            self.SPLIT_50_30_20: "50% / 30% / 20%",
        }[self]

class RoleStatus(models.TextChoices):
    ASSIGNED = "assigned", "Assigned"
    OPEN = "open", "Open"
    COMPLETED = "completed", "Completed"

class ProposalStatus(models.TextChoices):
    # Initial Stages
    SENT = "sent", "Sent"
    
    # Engagement Tracking
    REVIEWING = "reviewing", "In Review" # when the cretor opens the proposal
    
    # Active Discussion
    NEGOTIATING = "negotiating", "Negotiation"
    
    
    # Final Outcomes
    ACCEPTED = "accepted", "Accepted"
    REJECTED = "rejected", "Rejected"
    WITHDRAWN = "withdrawn", "Withdrawn"
    
class AssignmentStatus(models.TextChoices):
    ONGOING = "ongoing", "Ongoing"
    COMPLETED = "completed", "Completed"
    WITHDRAWN = "withdrawn", "Withdrawn"
    REVISIONS_PENDING = "revisions_pending", "Revisions Requested"