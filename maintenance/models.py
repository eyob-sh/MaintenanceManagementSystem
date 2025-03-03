from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.db.models import UniqueConstraint
from django.apps import apps
from django.db.models import JSONField




# Create your models here.

class Branch(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    # Define choices for departments
   

    # Define choices for roles
    ROLE_CHOICES = [
        ('MD manager', 'Maintenance Department Manager'),
        ('TEC', 'Technician'),
        ('MO', 'Maintenance Oversight'),
        ('CO', 'Chemical Oversight'),
        ('CL', 'Client'),
        ('AD', 'Admin'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    branch = models.ForeignKey('Branch', on_delete=models.PROTECT)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, null=True)

    def __str__(self):
        return self.user.username
    


# class MaintenanceTask(models.Model):

#     equipment_type = models.CharField(
#         help_text="Enter a type of maintenance "
#                   "(e.g., 'Software Installation').",
#         max_length=255,
#         unique=True,
#     )
#     # branch = models.ForeignKey('Branch' , on_delete=models.PROTECT)

#     description = models.TextField(
#         blank=True,
#         help_text='Enter a description of the maintenance type.',
#     )

#     class Meta:
#         ordering = ['equipment_type']

#     def __str__(self):
#         return self.equipment_type


class MaintenanceTask(models.Model):
    equipment_type = models.CharField(
        help_text="Enter a type of maintenance (e.g., 'Software Installation').",
        max_length=255,
        unique=True,
    )
    description = models.TextField(
        blank=True,
        help_text='Enter a description of the maintenance type.',
    )

    class Meta:
        ordering = ['equipment_type']

    def __str__(self):
        return self.equipment_type

class TaskGroup(models.Model):
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('biannually', 'Biannually'),
        ('annually', 'Annually'),
    ]

    maintenance_task = models.ForeignKey(MaintenanceTask, on_delete=models.CASCADE, related_name='task_groups')
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)

    def __str__(self):
        return f"{self.maintenance_task.equipment_type} - {self.get_frequency_display()}"
    


class Task(models.Model):
    task_group = models.ForeignKey(TaskGroup, on_delete=models.CASCADE, related_name='tasks')
    description = models.TextField(help_text='Enter a description of the task.')


    def __str__(self):
        return self.description


class Manufacturer(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    site= models.ForeignKey('Branch', on_delete=models.PROTECT)
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Equipment(models.Model):
    STATUS_CHOICES = [
        ('operational', 'Operational'),
        ('non_operational', 'Non Operational'),
        ('under_maintenance', 'Under Maintenance'),
    ]

    name = models.CharField(max_length=100)
    equipment_type = models.CharField(max_length=50)
    manufacturer = models.ForeignKey('Manufacturer', on_delete=models.PROTECT)
    model_number = models.CharField(max_length=50)
    serial_number = models.CharField(max_length=50)
    branch = models.ForeignKey('Branch', on_delete=models.PROTECT)
    location = models.CharField(max_length=50)
    installation_date = models.DateField()
    maintenance_interval_years = models.PositiveIntegerField(default=0)
    maintenance_interval_months = models.PositiveIntegerField(default=0)
    maintenance_interval_weeks = models.PositiveIntegerField(default=0)
    maintenance_interval_days = models.PositiveIntegerField(default=0)
    last_maintenance_date = models.DateField(null=True, blank=True)
    next_maintenance_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='operational')
    remark = models.TextField(blank=True)

    def calculate_next_maintenance_date(self):
        from datetime import timedelta
        next_date = self.installation_date
        next_date += timedelta(days=self.maintenance_interval_days)
        next_date += timedelta(weeks=self.maintenance_interval_weeks)
        next_date += timedelta(days=30 * self.maintenance_interval_months)
        next_date += timedelta(days=365 * self.maintenance_interval_years)
        return next_date

    def save(self, *args, **kwargs):
        # Set the next maintenance date only when the instance is created
        if not self.pk:  # Check if the instance is being created
            self.next_maintenance_date = self.calculate_next_maintenance_date()
        super().save(*args, **kwargs)  # Call the original save() method

    def __str__(self):
        return f"{self.name} ({self.equipment_type} -- {self.serial_number})"
    

class SparePart(models.Model):
    name = models.CharField(max_length=255)     # Name of the spare part
    branch = models.ForeignKey('Branch', on_delete=models.PROTECT)

    store = models.CharField(max_length=255)     # Store name
    quantity = models.IntegerField()              # Quantity left in stock
    description = models.TextField(blank=True)    # Description of the spare part
    part_number = models.CharField(max_length=100)  # Unique part identifier
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price of the spare part
    date_added = models.DateField(auto_now_add=True)  # Date when the part was added
    last_updated = models.DateField(auto_now=True)  # Date when the part was last updated
    last_restock_date = models.DateTimeField(null=True)
    
    

    def __str__(self):
        return f"{self.name} ({self.quantity} left) - {self.store}"
    
class RestockSparePart(models.Model):
    spare_part = models.ForeignKey(SparePart, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=0)
    restock_date = models.DateTimeField(auto_now_add=True)
    attachment = models.FileField(upload_to='restock_attachments/', null=True, blank=True)  # Optional attachment

    def __str__(self):
        return f"Restock {self.quantity} units of {self.spare_part.name} on {self.restock_date}"
    

    
class WorkOrder(models.Model):
    requester = models.ForeignKey(
        User,  # Use the built-in User model
        on_delete=models.PROTECT,
        related_name='work_orders',
        help_text='The user requesting the maintenance.',
    )
    branch = models.ForeignKey('Branch', on_delete=models.PROTECT)

    equipment = models.ForeignKey(
        'Equipment',
        on_delete=models.PROTECT,
        help_text='Select the equipment that needs maintenance.',
    )
    
    assigned_technicians = models.ManyToManyField(User)
    spare_parts = models.ManyToManyField('SparePart', through='SparePartUsage')

    
    location = models.CharField(max_length=40, null=True)
    
    description = models.TextField(
        help_text='Describe the maintenance needed.',
    )
    status = models.CharField(
        choices=[
            ('Pending', 'Pending'),
            ('Accepted', 'Accepted'),
            ('Complete', 'Complete'),
            ('Approved', 'Approved'),
        ],
        default='Pending',
        help_text='Current status of the work order.',
        max_length=15,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='The date and time when the work order was created.',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='The date and time when the work order was last updated.',
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Work Order'
        verbose_name_plural = 'Work Orders'

    def __str__(self):
        return f'Work Order #{self.id} - {self.equipment}'

class MaintenanceRecord(models.Model):
    STATUS_CHOICES = [
        ('Not Started', 'Not Started'),
        ('Accepted', 'Accepted'),
        ('In Progress', 'In Progress'),
        ('Complete', 'Complete'),
        ('Approved', 'Approved'),
        ('Failed', 'Failed'),
    ]

    equipment = models.ForeignKey('Equipment', on_delete=models.PROTECT)
    assigned_technicians = models.ManyToManyField(User, related_name='maintenance_records')
    branch = models.ForeignKey('Branch', on_delete=models.PROTECT)
    maintenance_task = models.ForeignKey('MaintenanceTask', on_delete=models.PROTECT, null=True)
    spare_parts = models.ManyToManyField('SparePart', through='SparePartUsage')
    remark = models.TextField(blank=True, null=True)
    procedure = models.TextField(blank=True, null=True)
    problems = models.TextField(blank=True, null=True)
    status = models.CharField(choices=STATUS_CHOICES, default='Not Started', max_length=15)
    datetime = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_maintenance')

    def __str__(self):
        return f'{self.equipment} - {self.maintenance_task} ({self.datetime.date()})'
        
    
class SparePartUsage(models.Model):
    maintenance_record = models.ForeignKey(MaintenanceRecord, on_delete=models.CASCADE, null=True)
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, null=True)
    spare_part = models.ForeignKey(SparePart, on_delete=models.CASCADE)
    quantity_used = models.IntegerField()  # Quantity of the spare part used
    

class DecommissionedEquipment(models.Model):
    equipment = models.OneToOneField('Equipment', on_delete=models.CASCADE)
    decommission_reason = models.TextField(blank=True, null=True)
    decommission_date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.equipment.name} - Decommissioned on {self.decommission_date}"
    




class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=40, null= True)
    message = models.CharField(max_length=255)
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    url = models.URLField(blank=True, null=True)  # Optional: Link to a specific page

    def __str__(self):
        return f'{self.user.username} - {self.message}'




