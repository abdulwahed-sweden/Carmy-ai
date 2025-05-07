from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Check if a profile already exists to prevent integrity error
        if not hasattr(instance, 'profile'):
            UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Make sure the profile exists before trying to save it
    if hasattr(instance, 'profile'):
        instance.profile.save()