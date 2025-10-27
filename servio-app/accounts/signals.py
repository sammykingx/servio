from django.db.models.signals import post_save
from django.dispatch import receiver
from .models.profile import UserProfile
from django.conf import settings

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

