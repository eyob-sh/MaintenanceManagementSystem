import logging
from django.apps import AppConfig
from django.core.management import call_command
from apscheduler.schedulers.background import BackgroundScheduler
from django.db.models.signals import post_migrate

logger = logging.getLogger(__name__)

class MaintenanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'maintenance'

    def ready(self):
        logger.info("MaintenanceConfig.ready() called.")  # Add this line
        # Connect the scheduler setup to the apps.ready signal
        from django.db.models.signals import post_migrate
        post_migrate.connect(self.setup_scheduler, sender=self)
        logger.info("Scheduler setup connected to post_migrate signal.")

    def setup_scheduler(self, **kwargs):
        # Ensure the app registry is ready
        from .models import SchedulerLock

        logger.info("Setting up scheduler...")

        # Create a database lock to ensure only one scheduler instance runs
        lock, created = SchedulerLock.objects.get_or_create(id=1)
        if not lock.locked:
            lock.locked = True
            lock.save()

            # Start the scheduler
            scheduler = BackgroundScheduler()
            scheduler.add_job(
                self.run_maintenance_check,  # Use a method instead of call_command
                'cron',
                minute='*',  # Run every minute
                id='check_maintenance_due',
            )
            scheduler.start()
            logger.info("Scheduler started successfully.")
        else:
            logger.info("Scheduler is already running.")

    def run_maintenance_check(self):
        # Call the management command directly
        from django.core.management import call_command
        call_command('check_maintenance_due')