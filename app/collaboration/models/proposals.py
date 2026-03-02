from django.db import models
from django.conf import settings
from django.utils import timezone
from uuid6 import uuid7
from .choices import ProposalStatus


class Proposal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)

    gig = models.ForeignKey(
        "collaboration.Gig",
        on_delete=models.PROTECT,
        related_name="proposals",
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="proposals",
    )

    status = models.CharField(
        max_length=20,
        choices=ProposalStatus.choices,
        default=ProposalStatus.SENT,
    )

    total_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=(
            "The worth of the user's proposal (summation of role amounts). "
            "This is filled after the proposal has been accepted."
        )
    )
    
    is_negotiating = models.BooleanField(default=False)
    sent_at = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "proposal"
        verbose_name = "Project Proposal"
        verbose_name_plural = "Project Proposals"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["gig", "sender"],
                name="unique_sender_proposal_per_gig",
            )
        ]
        indexes = [
            models.Index(fields=['sender', 'status'], name='proposal_sender_status_idx'),
            models.Index(fields=['gig', 'status'], name='proposal_gig_status_idx'),
            models.Index(fields=['sender', 'gig'], name='proposal_sender_gig_idx'),
        ]
        
    @property
    def sent_ago(self):
        if not self.sent_at:
            return ""

        now = timezone.now()
        diff = now - self.sent_at
        seconds = int(diff.total_seconds())

        # Seconds
        if seconds < 60:
            return f"{seconds} second{'s' if seconds != 1 else ''}"

        # Minutes
        minutes = seconds // 60
        if minutes < 60:
            return f"{minutes} minute{'s' if minutes != 1 else ''}"

        # Hours
        hours = minutes // 60
        if hours < 24:
            return f"{hours} hour{'s' if hours != 1 else ''}"

        # Days
        days = hours // 24
        if days < 7:
            return f"{days} day{'s' if days != 1 else ''}"

        # Weeks (7–29 days)
        if days < 30:
            weeks = days // 7
            return f"{weeks} week{'s' if weeks != 1 else ''}"

        # Months (30–364 days)
        if days < 365:
            months = days // 30
            return f"{months} month{'s' if months != 1 else ''}"

        # Years
        years = days // 365
        return f"{years} year{'s' if years != 1 else ''}"