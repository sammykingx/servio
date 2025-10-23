from django.db import models
from django.conf import settings


class Address(models.Model):
    """
    Stores user and profile-related address information.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, 
            on_delete=models.CASCADE,
            to_field="email",
            related_name="addresses"
        )
    street = models.CharField(max_length=60)
    street_line_2 = models.CharField(max_length=60, blank=True)
    city = models.CharField(max_length=20)
    province = models.CharField(max_length=20)
    postal_code = models.CharField(max_length=13)
    label = models.CharField(max_length=20, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    is_default = models.BooleanField(default=False)
    is_business_address = models.BooleanField(default=False)
    # connect the user and profile