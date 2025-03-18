# signals.py
from django.dispatch import Signal
from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Notification

# Create a custom signal
notification_created = Signal()

# Connect the signal to a receiver
@receiver(post_save, sender=Notification)
def notify_client(sender, instance, created, **kwargs):
    if created:
        # Trigger the custom signal
        notification_created.send(sender=sender, notification=instance)