from django.db import models
from .choices import WorkMode, RoleStatus
from uuid6 import uuid7


class GigRole(models.Model):
    """
        Represents a specific role required for a Gig/Project.

        Each Gig can have multiple roles associated with it, specifying
        the type of professional needed, the budget, workload, quantity,
        and status of the role.
    """
    id = models.UUIDField(primary_key=True, default=uuid7)
    gig = models.ForeignKey(
        "collaboration.Gig",
        on_delete=models.PROTECT,
        related_name="required_roles",
    )
    niche = models.ForeignKey(
        "collaboration.GigCategory",
        on_delete=models.PROTECT,
        related_name="roles"
    )
    niche_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Optional specific role title (e.g. Senior Frontend Engineer)"
    )
    role_id = models.PositiveIntegerField(
        null=True,
        help_text="Identifier for the subcategory under the main category"
    )
    role_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Optional specific role title (e.g. Senior Frontend Engineer)"
    )
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    workload = models.CharField(
        max_length=40,
        choices=WorkMode.choices,
        default=WorkMode.FIXED_HOURS,
    )
    description = models.TextField(blank=True)
    slots = models.PositiveIntegerField(default=1)
    status = models.CharField(
        max_length=40,
        choices=RoleStatus.choices,
        default=RoleStatus.OPEN
    )
    is_negotiable = models.BooleanField(
        default=False,
        help_text="Indicates if the budget is negotiable"
    )
    show_role_budget = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "collaboration_gig_roles"
        verbose_name = "Gig Role"
        verbose_name_plural = "Gig Roles"
        indexes = [
            models.Index(fields=["gig", "status"]),
            models.Index(fields=["status"]),
            models.Index(fields=["niche"]),
        ]
        
        
    def is_open(self):
        """
            Returns True if the role is currently open for applications.
        """
        return self.status == RoleStatus.OPEN

    def is_assigned(self):
        """
            Returns True if the role has been assigned to someone.
        """
        return self.status == RoleStatus.ASSIGNED

    def total_budget(self):
        """
        Returns the total budget considering quantity.
        """
        return self.budget * self.quantity

    def role_description(self):
        """
            Returns a human-readable description combining role title, niche, and status.
        """
        title = self.role_name or self.niche_name
        return f"{title} - {self.status} - Qty: {self.slots}"
    