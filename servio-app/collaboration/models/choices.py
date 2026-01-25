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

class RoleStatus(models.TextChoices):
    ASSIGNED = "assigned", "Assigned"
    OPEN = "open", "Open"
    COMPLETED = "completed", "Completed"

class ApplicationStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    ACCEPTED = "accepted", "Accepted"
    NEGOTIATING = "negotiating", "Negotiating"
    REJECTED = "rejected", "Rejected"
    WITHDRAWN = "withdrawn", "Withdrawn"
    
class AssignmentStatus(models.TextChoices):
    ONGOING = "ongoing", "Ongoing"
    COMPLETED = "completed", "Completed"
    WITHDRAWN = "withdrawn", "Withdrawn"