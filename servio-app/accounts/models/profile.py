from django.db import models
from django.conf import settings


class UserProfile(models.Model):
    """
    Extended profile for AuthUser (One-to-One relationship).
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        to_field="email", 
        on_delete=models.CASCADE, 
        related_name="profile",
    )
    mobile_num = models.CharField(max_length=18, unique=True, blank=True, null=True)
    alt_mobile_num = models.CharField(max_length=20, blank=True, null=True)
    avatar_url = models.ImageField(upload_to='avatars/', null=True, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    is_business_owner = models.BooleanField(default=False)
    # role = models.CharField(choices=())
    
    class Meta:
        db_table = "user_profiles"