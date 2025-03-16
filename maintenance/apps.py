import logging
from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler
from threading import Thread
import time
import os
import atexit

logger = logging.getLogger(__name__)

class MaintenanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'maintenance'

    def ready(self):
        # Ensure the scheduler setup runs only once
        if os.environ.get('RUN_MAIN') == 'true':
            logger.info("MaintenanceConfig.ready() called.")
            print("MaintenanceConfig.ready() called.")  # Debug print statement

            # Delay the scheduler setup to avoid database access during app initialization
            Thread(target=self.delayed_scheduler_setup).start()

    def delayed_scheduler_setup(self):
        """
        Delay the scheduler setup to ensure the database is ready.
        """
        # Wait for 5 seconds to ensure the server is fully ready
        time.sleep(5)
        self.setup_scheduler()

    def setup_scheduler(self):
        from .models import SchedulerLock

        logger.info("Setting up scheduler...")
        print("Setting up scheduler...")  # Debug print statement

        # Create a database lock to ensure only one scheduler instance runs
        lock, created = SchedulerLock.objects.get_or_create(id=1)
        if not lock.locked:
            lock.locked = True
            lock.save()

            # Start the scheduler
            self.scheduler = BackgroundScheduler()
            self.scheduler.add_job(
                self.run_maintenance_check,  # Use a method instead of call_command
                'interval',
                seconds=5,  # Run every 5 seconds for testing
                id='check_maintenance_due',
            )
            self.scheduler.start()
            logger.info("Scheduler started successfully.")
            print("Scheduler started successfully.")  # Debug print statement

            # Register a shutdown hook to release the lock
            atexit.register(self.release_lock)
        else:
            logger.info("Scheduler is already running.")
            print("Scheduler is already running.")  # Debug print statement

    def release_lock(self):
        """
        Release the lock when the application shuts down.
        """
        from .models import SchedulerLock
        lock = SchedulerLock.objects.get(id=1)
        lock.locked = False
        lock.save()
        logger.info("Scheduler lock released.")
        print("Scheduler lock released.")  # Debug print statement

    def run_maintenance_check(self):
        logger.info("Scheduler is running! Checking for maintenance due...")
        print("Scheduler is running! Checking for maintenance due...")  # Debug print statement
        from django.core.management import call_command
        call_command('check_maintenance_due')