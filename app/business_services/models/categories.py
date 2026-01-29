from django.db import models


class ServiceCategory(models.Model):
    business_id = models.ForeignKey(
        "business_accounts.BusinessAccount",
        on_delete=models.CASCADE,
        related_name="categories",
    )

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "service_categories"
        constraints = [
            models.UniqueConstraint(
                fields=["business_id", "name"],
                name="unique_category_per_business",
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.business_id})"