# from django.core.management.base import BaseCommand
# from django.utils import timezone
# from django.core.mail import send_mail
# from django.conf import settings
# from maintenance.models import Equipment, User
# from datetime import timedelta

# class Command(BaseCommand):
#     help = 'Checks for equipment due for maintenance and sends notifications.'

#     def handle(self, *args, **kwargs):
#         today = timezone.now().date()
#         due_date = today + timedelta(days=5)

#         # Filter equipment due for maintenance within the next 5 days
#         due_equipment = Equipment.objects.filter(
#             next_maintenance_date__lte=due_date,
#             next_maintenance_date__gte=today
#         )

#         # Notify MD managers in the same branch as the equipment
#         for equipment in due_equipment:
#             md_managers = User.objects.filter(
#                 branch=equipment.branch,
#                 role__in=['MD manager', 'Maintenance Department Manager']
#             )

#             for manager in md_managers:
#                 send_mail(
#                     subject=f"Maintenance Due for {equipment.name}",
#                     message=f"Equipment {equipment.name} is due for maintenance on {equipment.next_maintenance_date}.",
#                     from_email=settings.DEFAULT_FROM_EMAIL,
#                     recipient_list=[manager.email],
#                     fail_silently=False,
#                 )

#         self.stdout.write(self.style.SUCCESS('Successfully checked for maintenance due.'))

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from maintenance.models import Equipment, UserProfile  # Adjust the import according to your app structure

class Command(BaseCommand):
    help = 'Checks for equipment due for maintenance and sends notifications.'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        due_date = today + timedelta(days=5)

        # Filter equipment due for maintenance within the next 5 days
        due_equipment = Equipment.objects.filter(
            next_maintenance_date__lte=due_date,
            next_maintenance_date__gte=today
        )

        # Notify MD managers in the same branch as the equipment
        for equipment in due_equipment:
            md_managers = UserProfile.objects.filter(
                branch=equipment.branch,
                role__in=['MD manager', 'Maintenance Department Manager']
            ).select_related('user')  # Use select_related to fetch the User data efficiently

            for manager in md_managers:
                send_mail(
                    subject=f"Maintenance Due for {equipment.name}",
                    message=f"Equipment {equipment.name} is due for maintenance on {equipment.next_maintenance_date}.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[manager.user.email],  # Access the email through the User object
                    fail_silently=False,
                )

        self.stdout.write(self.style.SUCCESS('Successfully checked for maintenance due.'))