from django.core.management.base import BaseCommand
from django.utils import timezone
from django.template.loader import render_to_string
from .models import Equipment, SparePart, Notification, User

class Command(BaseCommand):
    help = 'Checks for equipment due for maintenance and low spare parts, and sends notifications based on branch.'

    def handle(self, *args, **kwargs):
        # Check equipment with next_maintenance_date less than 5 days
        today = timezone.now().date()
        five_days_later = today + timezone.timedelta(days=5)
        equipment_due_for_maintenance = Equipment.objects.filter(next_maintenance_date__lte=five_days_later)

        # Check spare parts with quantity less than 5
        low_spare_parts = SparePart.objects.filter(quantity__lt=5)

        # Send notifications for equipment due for maintenance
        if equipment_due_for_maintenance.exists():
            for equipment in equipment_due_for_maintenance:
                # Get MD managers in the same branch as the equipment
                users_to_notify = User.objects.filter(
                    userprofile__role='MD manager',
                    userprofile__branch=equipment.branch,
                )
                for user in users_to_notify:
                    message = render_to_string('maintenance_due.html', {
                        'user': user,
                        'equipment_list': [equipment],  # Send notification for this specific equipment
                    })
                    Notification.objects.create(
                        user=user,
                        type = "low_maintenance",
                        message=message,
                    )
                    self.stdout.write(self.style.SUCCESS(
                        f'Notification sent to {user.get_full_name()} for equipment {equipment.name} due for maintenance.'
                    ))

        # Send notifications for low spare parts
        if low_spare_parts.exists():
            for spare_part in low_spare_parts:
                # Get MD managers in the same branch as the spare part
                users_to_notify = User.objects.filter(
                    userprofile__role='MD manager',
                    userprofile__branch=spare_part.branch,
                )
                for user in users_to_notify:
                    message = render_to_string('low_spare_part.html', {
                        'user': user,
                        
                        'spare_parts': [spare_part],  # Send notification for this specific spare part
                    })
                    Notification.objects.create(
                        user=user,
                        type = "low_spare_part",
                        message=message,
                    )
                    self.stdout.write(self.style.SUCCESS(
                        f'Notification sent to {user.get_full_name()} for low spare part {spare_part.name}.'
                    ))