from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from uuid6 import uuid7
from .choices import ApplicationStatus, RoleStatus


class GigApplication(models.Model):
    """
        Represents a user's application to work on a specific GigRole.

        Each application links a user to a GigRole and includes their proposed
        amount and an optional message. The application has a status that tracks
        whether it is pending, accepted, rejected, or withdrawn.
    """

    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)

    gig_role = models.ForeignKey(
        "collaboration.GigRole",
        on_delete=models.PROTECT,
        related_name="applications",
        help_text="The specific role this application is for",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="gig_applications",
        help_text="The user applying for the role",
    )

    proposed_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="The amount proposed by the applicant for this role",
    )

    final_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="The agreed amount if the application is accepted",
    )

    message = models.TextField(
        blank=True,
        null=True,
        help_text="Optional message from the applicant",
    )

    status = models.CharField(
        max_length=20,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.PENDING,
        help_text="The current status of the application",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "collaboration_gig_applications"
        verbose_name = "Gig Application"
        verbose_name_plural = "Gig Applications"
        ordering = ["-created_at"]
        unique_together = ("gig_role", "user")  # Prevent duplicate applications

    def __str__(self):
        return f"Application by {self.user} for {self.gig_role}"

    def __repr__(self):
        return f"<GigApplication id={self.id} user={self.user.email} role={self.gig_role.role_title} status={self.status}>"

    def is_pending(self):
        """Return True if the application is still pending."""
        return self.status == ApplicationStatus.PENDING

    def is_accepted(self):
        """Return True if the application has been accepted."""
        return self.status == ApplicationStatus.ACCEPTED

    def is_rejected(self):
        """Return True if the application has been rejected."""
        return self.status == ApplicationStatus.REJECTED

    def is_withdrawn(self):
        """Return True if the applicant has withdrawn."""
        return self.status == ApplicationStatus.WITHDRAWN
    
    def clean(self):
        """
        Ensure that applications can only be created if the GigRole is open.
        """
        if self.gig_role.status != RoleStatus.OPEN:
            raise ValidationError(
                f"Cannot apply to this role because its status is '{self.gig_role.status}'."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def accept_offer(self, final_amount=None):
        """
        Accept this application:
        1. Set the application status to ACCEPTED
        2. Update the final_amount if provided
        3. Check if the gig role can still accept an assignment
        4. Create a GigAssignment
        5. Update GigRole status if fully assigned
        """

        # Ensure role has available slots
        from django.db.models import F
        from django.db import transaction
        from django.apps import apps
        
        GigAssignment = apps.get_model("collaboration", "GigAssignment")
        
        
        if self.gig_role.assignments.count() > self.gig_role.slots:
            raise ValidationError("Gig role has no available slots left.")

        with transaction.atomic():
            # Update the gig application
            self.status = ApplicationStatus.ACCEPTED
            if final_amount:
                self.final_amount = final_amount
            self.save(update_fields=["status", "final_amount", "updated_at"])

            # Create the assignment
            assignment = GigAssignment.objects.create(
                gig_role=self.gig_role,
                professional=self.user,
                agreed_amount=self.final_amount or self.proposed_amount,
                started_at=None,
                completed_at=None
            )

            # Update role status if fully assigned
            if self.gig_role.assignments.count() == self.gig_role.slots:
                self.gig_role.status = RoleStatus.ASSIGNED
                self.gig_role.save(update_fields=["status", "updated_at"])

        return assignment