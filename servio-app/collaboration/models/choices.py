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

class WorkMode(models.TextChoices):
    FIXED_HOURS = "fixed_hours", "Fixed hours"
    FLEXIBLE = "flexible", "Flexible (result-based)"

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