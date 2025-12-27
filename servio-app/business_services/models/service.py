from django.db import models


from django.db import models
from django.core.exceptions import ValidationError


class Services(models.Model):
    business_id = models.ForeignKey(
        "business_accounts.BusinessAccount",
        on_delete=models.CASCADE,
        related_name="services",
    )

    category = models.ForeignKey(
        "business_services.ServiceCategory",
        on_delete=models.PROTECT,
        related_name="services",
    )

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_minutes = models.PositiveIntegerField()

    is_active = models.BooleanField(default=True)
    is_bookable = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "provider_services"
        constraints = [
            models.UniqueConstraint(
                fields=["business_id", "name"],
                name="unique_service_name_per_business",
            )
        ]

    def clean(self):
        if self.category.business_id != self.business_id:
            raise ValidationError(
                "Service category must belong to the same business"
            )

    def __str__(self):
        return f"{self.name} - {self.business.business_name}"
