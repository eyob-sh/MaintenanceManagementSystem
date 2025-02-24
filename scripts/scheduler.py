from apscheduler.schedulers.blocking import BlockingScheduler
from django.core.management import call_command
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MaintenanceManagementSystem.settings')  # Change to your settings module
django.setup()

def check_maintenance_due():
    call_command('check_maintenance_due')

if __name__ == '__main__':
    scheduler = BlockingScheduler()
    # Schedule to run daily at 9 AM
    scheduler.add_job(check_maintenance_due, 'interval', minutes=1)
    scheduler.start()