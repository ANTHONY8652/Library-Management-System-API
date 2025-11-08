from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

@receiver(post_save, sender=User)
def user_registered_signal(sender, instance, created, **kwargs):
    if created:
        print(f'New user registered: {instance.username}')