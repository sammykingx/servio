from django.db import transaction
from django.db.models.signals import post_save
from django.contrib.auth.models import Group
from allauth.account.signals import email_confirmed
from django.dispatch import receiver
from .models.profile import UserProfile
from notifications.models.notification_channels import NotificationChannels
from django.conf import settings


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    if created:
        try:
            with transaction.atomic():
                UserProfile.objects.create(user=instance)
                NotificationChannels.objects.create(user=instance)
        except Exception as e:
            # log for prod, print for dev or short term
            print(e)
            # raise
            

@receiver(post_save, sender=UserProfile)
def assign_group_on_profile_save(sender, instance, **kwargs):
    user = instance.user
    user.groups.clear()

    try:
        group = Group.objects.get(name=instance.role)
        user.groups.add(group)
    except Group.DoesNotExist:
        pass


@receiver(email_confirmed)
def mark_user_verified(request, email_address, **kwargs):
    user = email_address.user
    user.is_verified = True
    user.save(update_fields=["is_verified"])
