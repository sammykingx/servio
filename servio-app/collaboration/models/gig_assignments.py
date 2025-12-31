from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from .choices import AssignmentStatus
from uuid6 import uuid7


class GigAssignment(models.Model):
    """
    Represents the assignment of a professional to a specific GigRole.

    Each assignment tracks the agreed amount, work hours, and timestamps
    for start and completion. The number of assignments for a role
    cannot exceed the slots defined in the GigRole.
    """

    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)

    gig_role = models.ForeignKey(
        "collaboration.GigRole",
        on_delete=models.PROTECT,
        related_name="assignments",
        help_text="The role this assignment belongs to"
    )

    professional = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="gig_assignments",
        help_text="The user assigned to this role"
    )

    agreed_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="The final agreed amount for this assignment"
    )

    # agreed_hours_start = models.DecimalField(
    #     max_digits=5,
    #     decimal_places=2,
    #     null=True,
    #     blank=True,
    #     help_text="Start of agreed hours (if applicable)"
    # )

    # agreed_hours_end = models.DecimalField(
    #     max_digits=5,
    #     decimal_places=2,
    #     null=True,
    #     blank=True,
    #     help_text="End of agreed hours (if applicable)"
    # )

    started_at = models.DateTimeField(null=True, blank=True)
    deadline = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_withdrawn = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20,
        choices=AssignmentStatus.choices,
        default=AssignmentStatus.ONGOING,
        help_text="Current status of the assignment"
    )

    class Meta:
        db_table = "collaboration_gig_assignments"
        verbose_name = "Gig Assignment"
        verbose_name_plural = "Gig Assignments"
        ordering = ["-created_at"]
        unique_together = ("gig_role", "professional")  # prevent duplicate assignment

    def __str__(self):
        return f"{self.professional} assigned to {self.gig_role.role_title}"

    def __repr__(self):
        return f"<GigAssignment id={self.id} professional={self.professional.email} role={self.gig_role.role_title}>"

    def clean(self):
        """
        Ensure the number of assignments does not exceed the slots of the GigRole.
        """
        current_count = self.gig_role.assignments.exclude(id=self.id).count()
        if current_count >= self.gig_role.slots:
            raise ValidationError(
                f"Cannot assign more than {self.gig_role.slots} professionals "
                f"to this role ({self.gig_role.role_title})."
            )

    def save(self, *args, **kwargs):
        # Run validation before saving
        self.full_clean()
        super().save(*args, **kwargs)

    def mark_started(self, timestamp=None):
        """Mark the assignment as started."""
        import django.utils.timezone as timezone
        self.started_at = timestamp or timezone.now()
        self.save(update_fields=["started_at"])

    def mark_completed(self, timestamp=None):
        """Mark the assignment as completed."""
        import django.utils.timezone as timezone
        self.completed_at = timestamp or timezone.now()
        self.save(update_fields=["completed_at"])

    @classmethod
    def assignments_for_role(cls, gig_role):
        """Return all assignments for a given GigRole."""
        return cls.objects.filter(gig_role=gig_role)

    @classmethod
    def is_role_fully_assigned(cls, gig_role):
        """
        Check if the number of assignments has reached the slots for this role.
        Returns True if fully assigned.
        """
        return cls.assignments_for_role(gig_role).count() >= gig_role.slots