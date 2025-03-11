from django.core.management.base import BaseCommand
from django.utils import timezone
from django.template.loader import render_to_string
from django.conf import settings
from maintenance.models import Equipment, Notification
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Checks for due maintenance dates and sends notifications'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        due_in_5_days = today + timezone.timedelta(days=5)

        # Fetch equipment due for maintenance within the next 5 days
        due_equipment = Equipment.objects.filter(
            next_monthly_maintenance_date__lte=due_in_5_days,
            last_notification_sent__lt=today,  # Ensure notification is sent only once
        ) | Equipment.objects.filter(
            next_biannual_maintenance_date__lte=due_in_5_days,
            last_notification_sent__lt=today,
        ) | Equipment.objects.filter(
            next_annual_maintenance_date__lte=due_in_5_days,
            last_notification_sent__lt=today,
        )

        if due_equipment.exists():
            self.stdout.write(f"Found {due_equipment.count()} equipment(s) due for maintenance.")
            for equipment in due_equipment:
                self.create_notifications(equipment)
                # Mark that a notification has been sent
                equipment.last_notification_sent = today
                equipment.save()
        else:
            self.stdout.write("No equipment due for maintenance in the next 5 days.")

    def create_notifications(self, equipment):
        # Create notifications for the manager and technician
        users_to_notify = [equipment.branch.manager, equipment.branch.technician]
        due_dates = {
            'monthly': equipment.next_monthly_maintenance_date,
            'biannual': equipment.next_biannual_maintenance_date,
            'annual': equipment.next_annual_maintenance_date,
        }

        for user in users_to_notify:
            for maintenance_type, due_date in due_dates.items():
                if due_date <= (timezone.now().date() + timezone.timedelta(days=5)):
                    message = (
                        f"Maintenance due for {equipment.name} ({maintenance_type}): {due_date}. "
                        f"Location: {equipment.location}, Branch: {equipment.branch.name}."
                    )
                    Notification.objects.create(
                        user=user,
                        type=f"{maintenance_type}_maintenance",
                        message=message,
                        url=f"/equipment/{equipment.id}/",  # Optional: Link to equipment detail page
                    )
                    self.stdout.write(f"Notification created for {user.username}: {message}")