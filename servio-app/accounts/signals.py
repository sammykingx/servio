from django.db import transaction
from django.db.models.signals import post_save
from allauth.account.signals import email_confirmed
from django.dispatch import receiver
from .models.profile import UserProfile
from django.conf import settings

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    if created:
        try:
            with transaction.atomic():
                UserProfile.objects.create(user=instance)
        except Exception as e:
            print(e)
            # raise
        # UserProfile.objects.create(user=instance)


@receiver(email_confirmed)
def mark_user_verified(request, email_address, **kwargs):
    user = email_address.user
    user.is_verified = True
    user.save(update_fields=['is_verified'])
