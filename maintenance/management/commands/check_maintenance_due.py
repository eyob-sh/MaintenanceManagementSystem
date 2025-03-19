from django.core.management.base import BaseCommand
from django.utils import timezone
from maintenance.models import Equipment, Notification
from django.contrib.auth.models import User
import logging
from django.db.models import Q
from maintenance.signals import notification_created


logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Checks for due maintenance dates and sends notifications'

    def handle(self, *args, **kwargs):
        logger.info("Running maintenance check...")
        today = timezone.now().date()
        due_in_5_days = today + timezone.timedelta(days=5)

        # Fetch equipment due for maintenance within the next 5 days
        due_equipment = Equipment.objects.filter(
            Q(next_monthly_maintenance_date__lte=due_in_5_days) &
            (Q(last_monthly_notification_sent__lt=today) | Q(last_monthly_notification_sent__isnull=True))
        ) | Equipment.objects.filter(
            Q(next_biannual_maintenance_date__lte=due_in_5_days) &
            (Q(last_biannual_notification_sent__lt=today) | Q(last_biannual_notification_sent__isnull=True))
        ) | Equipment.objects.filter(
            Q(next_annual_maintenance_date__lte=due_in_5_days) &
            (Q(last_annual_notification_sent__lt=today) | Q(last_annual_notification_sent__isnull=True))
        )

        if due_equipment.exists():
            self.stdout.write(f"Found {due_equipment.count()} equipment(s) due for maintenance.")
            for equipment in due_equipment:
                self.create_notifications(equipment)
        else:
            self.stdout.write("No equipment due for maintenance in the next 5 days.")

    def create_notifications(self, equipment):
        today = timezone.now().date()  # Define today here

        # Fetch users with roles 'TEC' and 'MD manager' in the same branch as the equipment
        users_to_notify = User.objects.filter(
            userprofile__branch=equipment.branch,  # Filter by branch
            userprofile__role__in=['TEC', 'MD manager']  # Filter by role
        ).distinct()

        due_dates = {
            'monthly': equipment.next_monthly_maintenance_date,
            'biannual': equipment.next_biannual_maintenance_date,
            'annual': equipment.next_annual_maintenance_date,
        }

        for user in users_to_notify:
            for maintenance_type, due_date in due_dates.items():
                if due_date <= (timezone.now().date() + timezone.timedelta(days=5)):
                    # Check if a notification has already been sent for this maintenance type
                    last_notification_sent_field = f"last_{maintenance_type}_notification_sent"
                    last_notification_sent = getattr(equipment, last_notification_sent_field)

                    if last_notification_sent is None or last_notification_sent < today:
                        message = (
                            f"Maintenance due for {equipment.name} ({maintenance_type}): {due_date}. "
                            f"Location: {equipment.location}, Branch: {equipment.branch.name}."
                        )
                        # Create the notification with type 'maintenance_due'
                        Notification.objects.create(
                            user=user,
                            type='maintenance_due',  # Set the type to 'maintenance_due'
                            message=message,
                            url=f"/equipment/{equipment.id}/",  # Optional: Link to equipment detail page
                        )
                        notification_created.send(sender=Notification)
                        self.stdout.write(f"Notification created for {user.username}: {message}")

                        # Update the last_notification_sent field for this maintenance type
                        setattr(equipment, last_notification_sent_field, today)
                        equipment.save()