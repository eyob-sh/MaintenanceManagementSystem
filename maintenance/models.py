from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.db.models import UniqueConstraint
from django.apps import apps
from django.db.models import JSONField
from datetime import timedelta 
from django.db.models import Sum





# Create your models here.

class Branch(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']  # Use '-' for descending order

    def __str__(self):
        return self.name
    

class UserProfile(models.Model):
    # Define choices for departments
   

    # Define choices for roles
    ROLE_CHOICES = [
        ('MD manager', 'Maintenance Department Manager'),
        ('TEC', 'Technician'),
        ('MO', 'Maintenance Oversight'),
        ('IM', 'Inventory Manager'),
       
        ('CL', 'Client'),
        ('AD', 'Admin'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    branch = models.ForeignKey('Branch', on_delete=models.PROTECT)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ['-created_at']  # Use '-' for descending order

    def __str__(self):
        return self.user.username
    




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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ['-created_at']  # Use '-' for descending order

    def __str__(self):
        return self.equipment_type

class TaskGroup(models.Model):
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'quarterly'),
        ('biannual', 'Biannual'),
        ('annual', 'Annual'),
    ]

    maintenance_task = models.ForeignKey(MaintenanceTask, on_delete=models.CASCADE, related_name='task_groups')
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    updated_at = models.DateTimeField(auto_now=True)



    def __str__(self):
        return f"{self.maintenance_task.equipment_type} - {self.get_frequency_display()}"
    


class Task(models.Model):
    task_group = models.ForeignKey(TaskGroup, on_delete=models.CASCADE, related_name='tasks')
    description = models.TextField(help_text='Enter a description of the task.')
    updated_at = models.DateTimeField(auto_now=True)



    def __str__(self):
        return self.description


class Manufacturer(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    site= models.ForeignKey('Branch', on_delete=models.PROTECT)
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ['-created_at']  # Use '-' for descending order
        unique_together = ('name', 'site')

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
    manufacturer = models.CharField(max_length=50, null= True, blank=True)
    model_number = models.CharField(max_length=50)
    serial_number = models.CharField(max_length=50)
    branch = models.ForeignKey('Branch', on_delete=models.PROTECT)
    location = models.CharField(max_length=50)
    installation_date = models.DateField()
    decommissioned = models.BooleanField(default=False)
    last_daily_maintenance_date = models.DateField(null=True, blank=True)
    next_daily_maintenance_date = models.DateField(null=True, blank=True)
    last_weekly_maintenance_date = models.DateField(null=True, blank=True)
    next_weekly_maintenance_date = models.DateField(null=True, blank=True)
    last_monthly_maintenance_date = models.DateField(null=True, blank=True)
    next_monthly_maintenance_date = models.DateField(null=True, blank=True)
    last_quarterly_maintenance_date = models.DateField(null=True, blank=True)
    next_quarterly_maintenance_date = models.DateField(null=True, blank=True)
    last_biannual_maintenance_date = models.DateField(null=True, blank=True)
    next_biannual_maintenance_date = models.DateField(null=True, blank=True)
    last_annual_maintenance_date = models.DateField(null=True, blank=True)
    next_annual_maintenance_date = models.DateField(null=True, blank=True)

    
    last_maintenance_date = models.DateField(null=True, blank=True)
    next_maintenance_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='operational')
    remark = models.TextField(blank=True)
    last_monthly_notification_sent = models.DateField(null=True, blank=True)
    last_quarterly_notification_sent = models.DateField(null=True, blank=True)
    last_biannual_notification_sent = models.DateField(null=True, blank=True)
    last_annual_notification_sent = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ['-created_at']  # Use '-' for descending order
        unique_together = [['equipment_type', 'serial_number']]  # Ensures uniqueness of the pair

    def calculate_next_maintenance_date(self,maintenance_type):
        """
        Calculate the next maintenance date based on the maintenance type.
        """
        today = self.installation_date

        if maintenance_type == 'daily':
            # For daily maintenance, add 1 day
            return today + timedelta(days=1)
        
        elif maintenance_type == 'weekly':
            # For weekly maintenance, add 1 week
            return today + timedelta(weeks=1)
        
        elif maintenance_type == 'monthly':
            # For monthly maintenance, add 1 month (approximated as 30 days)
            return today + timedelta(days=30)
        
        elif maintenance_type == 'quarterly':
            # For quarterly maintenance, add 3 month (approximated as 91 days)
            return today + timedelta(days=91)
        
        
        elif maintenance_type == 'annual':
            # For annual maintenance, add 1 year (approximated as 365 days)
            return today + timedelta(days=365)
        
        elif maintenance_type == 'biannual':
            # For biannual maintenance, add 6 months (approximated as 182 days)
            return today + timedelta(days=182)
        
        else:
            # Default fallback: return today + 1 day
            return today + timedelta(days=1)

    def save(self, *args, **kwargs):
        # Set the next maintenance date only when the instance is created
        if not self.pk:  # Check if the instance is being created
            self.next_weekly_maintenance_date = self.calculate_next_maintenance_date('weekly')
            self.next_monthly_maintenance_date = self.calculate_next_maintenance_date('monthly')
            self.next_quarterly_maintenance_date = self.calculate_next_maintenance_date('quarterly')
            self.next_biannual_maintenance_date = self.calculate_next_maintenance_date('biannual')
            self.next_annual_maintenance_date = self.calculate_next_maintenance_date('annual')

            


        super().save(*args, **kwargs)  # Call the original save() method

    def __str__(self):
        return f"{self.name} ({self.serial_number})"
    

class SparePart(models.Model):
    name = models.CharField(max_length=255)     # Name of the spare part
    branch = models.ForeignKey('Branch', on_delete=models.PROTECT)

    store = models.CharField(max_length=255)     # Store name
    quantity = models.IntegerField()              # Quantity left in stock
    description = models.TextField(blank=True)    # Description of the spare part
    part_number = models.CharField(max_length=100)  # Unique part identifier
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Price of the spare part
    date_added = models.DateField(auto_now_add=True)  # Date when the part was added
    last_updated = models.DateField(auto_now=True)  # Date when the part was last updated
    last_restock_date = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    min_quantity = models.IntegerField(default=0)  # Minimum quantity threshold for alerts
    is_active = models.BooleanField(default=True)  # To mark parts as active/inactive
    
    def get_available_quantity(self):
        """Returns quantity available after considering pending requests"""
        # Get all pending requests for this spare part
        pending_requests = SparePartRequest.objects.filter(
            spare_part=self,
            status__in=['Requested', 'Approved', 'Issued']
        ).aggregate(total=Sum('quantity_requested'))['total'] or 0
        
        return self.quantity - pending_requests

    

    class Meta:
        ordering = ['-created_at']  # Use '-' for descending order
    
    

    def __str__(self):
        return f"{self.name} ({self.quantity} left) - {self.store}"
    
class RestockSparePart(models.Model):
    spare_part = models.ForeignKey(SparePart, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=0)
    restock_date = models.DateTimeField(auto_now_add=True)
    attachment = models.FileField(upload_to='restock_attachments/', null=True, blank=True)  # Optional attachment
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ['-created_at']  # Use '-' for descending order

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
        null=True,
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
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name="Price"
    )

    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_work_order')
    rejected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='rejected_work_order')
    remark = models.TextField(blank=True, null=True)



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

    MAINTENANCE_TYPE_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'quarterly'),
        ('biannual', 'Biannual'),
        ('annual', 'Annual'),
    ]

    equipment = models.ForeignKey('Equipment', on_delete=models.PROTECT)
    assigned_technicians = models.ManyToManyField(User, related_name='maintenance_records')
    branch = models.ForeignKey('Branch', on_delete=models.PROTECT)
    maintenance_task = models.ForeignKey('MaintenanceTask', on_delete=models.PROTECT, null=True)
    maintenance_type = models.CharField(max_length=20, choices=MAINTENANCE_TYPE_CHOICES, null=True)  # New field
    spare_parts = models.ManyToManyField('SparePart', through='SparePartUsage')
    remark = models.TextField(blank=True, null=True)
    procedure = models.TextField(blank=True, null=True)
    problems = models.TextField(blank=True, null=True)
    status = models.CharField(choices=STATUS_CHOICES, default='Not Started', max_length=15)
    datetime = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_maintenance')
    rejected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='rejected_maintenance')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # New fields for task completion and technician acceptance
    accepted_by = models.ManyToManyField(User, related_name='accepted_maintenance', blank=True)
    completed_tasks = models.ManyToManyField('Task', through='TaskCompletion')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.equipment} - {self.maintenance_task} ({self.datetime.date()})'
class TaskCompletion(models.Model):
    maintenance_record = models.ForeignKey(MaintenanceRecord, on_delete=models.CASCADE)
    task = models.ForeignKey('Task', on_delete=models.CASCADE)
    completed_by = models.ForeignKey(User, on_delete=models.CASCADE,null=True, blank=True)
    remark = models.TextField(blank=True, null=True)  # Add this field for task remarks
    completed_at = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)  # New field

#---------------------------------------------added for inventory------------------------------------------

class SparePartRequest(models.Model):
    STATUS_CHOICES = [
        ('Requested', 'Requested'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Issued', 'Issued'),
        ('Received', 'Received'),
        ('Canceled', 'Canceled'),
        # ('Used', 'Used'),
        ('Return_Request', 'Return Request'),  # New status
        ('Return_Accepted', 'Accepted Returns'),    # New status
       
        ('Returned', 'Returned'),
        
    ]
    
    technician = models.ForeignKey(User, on_delete=models.CASCADE, related_name='spare_part_requests')
    inventory_manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_spare_part_requests')
    spare_part = models.ForeignKey(SparePart, on_delete=models.CASCADE)
    quantity_requested = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Requested')
    request_date = models.DateTimeField(auto_now_add=True)
    approval_date = models.DateTimeField(null=True, blank=True)
    issue_date = models.DateTimeField(null=True, blank=True)
    use_date = models.DateTimeField(null=True, blank=True)
    return_date = models.DateTimeField(null=True, blank=True)
    reason = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True)
    return_condition = models.TextField(blank=True)
    return_accepted = models.BooleanField(default=False)
    canceled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='canceled_requests')
    cancel_reason = models.TextField(blank=True)
    cancel_date = models.DateTimeField(null=True, blank=True)
    is_return_request = models.BooleanField(default=False)
    return_request_date = models.DateTimeField(null=True, blank=True)
    return_accepted_date = models.DateTimeField(null=True, blank=True)
    return_completed_date = models.DateTimeField(null=True, blank=True)
    attachment = models.FileField(upload_to='spare_part_request_attachments/', null=True, blank=True)
    @property
    def quantity_remaining(self):
        if self.status == 'Received':
            return self.quantity_requested - sum(
                transaction.quantity 
                for transaction in self.transactions.filter(
                    transaction_type__in=['Usage', 'Return']
                )
            )
        return 0
    
    def save(self, *args, **kwargs):
        # When status changes to Received, update TechnicianSparePart
        if self.pk:  # Only for existing instances
            old_status = SparePartRequest.objects.get(pk=self.pk).status
            if old_status != 'Received' and self.status == 'Received':
                tech_part, created = TechnicianSparePart.objects.get_or_create(
                    technician=self.technician,
                    spare_part=self.spare_part,
                    defaults={'received_quantity': self.quantity_requested, 'request': self}
                )
                if not created:
                    tech_part.received_quantity += self.quantity_requested
                    tech_part.save()
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-request_date']
    
    def __str__(self):
        return f"{self.spare_part.name} - {self.quantity_requested} ({self.status})"

class SparePartTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('Request', 'Request'),
        ('Approval', 'Approval'),
        ('Issuance', 'Issuance'),
        ('Usage', 'Usage'),
        ('Return', 'Return'),
        ('Cancellation', 'Cancellation'),
        ('Receipt', 'Receipt'),
    ]
    
    request = models.ForeignKey(SparePartRequest, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField()
    notes = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.request.spare_part.name}"
    
    def save(self, *args, **kwargs):
        # When usage is recorded, update TechnicianSparePart
        if self.transaction_type == 'Usage':
            tech_part = TechnicianSparePart.objects.get(
                technician=self.request.technician,
                spare_part=self.request.spare_part
            )
            tech_part.used_quantity += self.quantity
            tech_part.save()
        super().save(*args, **kwargs)



#----------------------------------------------------------------------------------------------------------



class SparePartUsage(models.Model):
    maintenance_record = models.ForeignKey(MaintenanceRecord, on_delete=models.CASCADE, null=True)
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, null=True)
    spare_part = models.ForeignKey(SparePart, on_delete=models.CASCADE)
    quantity_used = models.IntegerField()  # Quantity of the spare part used
    request = models.ForeignKey(SparePartRequest, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ['-created_at']  # Use '-' for descending order


class TechnicianSparePart(models.Model):
    technician = models.ForeignKey(User, on_delete=models.CASCADE)
    spare_part = models.ForeignKey(SparePart, on_delete=models.CASCADE)
    received_quantity = models.IntegerField(default=0)
    used_quantity = models.IntegerField(default=0)
    request = models.ForeignKey(  # Add this
        SparePartRequest, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='technician_inventory_records'
    )
    
    @property
    def available_quantity(self):
        return self.received_quantity - self.used_quantity
    
    def get_available_quantity(self):
        return self.received_quantity - self.used_quantity

    class Meta:
        unique_together = ('technician', 'spare_part')



class DecommissionedEquipment(models.Model):
    equipment = models.OneToOneField('Equipment', on_delete=models.CASCADE)
    decommission_reason = models.TextField(blank=True, null=True)
    decommission_date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ['-created_at']  # Use '-' for descending order

    def __str__(self):
        return f"{self.equipment.name} - Decommissioned on {self.decommission_date}"
    




class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=255, null= True)
    message = models.CharField(max_length=255)
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    url = models.URLField(blank=True, null=True)  # Optional: Link to a specific page
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    

    class Meta:
        ordering = ['-created_at']  # Use '-' for descending order

    def __str__(self):
        return f'{self.user.username} - {self.message}'





class SchedulerLock(models.Model):
    locked = models.BooleanField(default=False)

    def __str__(self):
        return f"Scheduler Lock (ID: {self.id}, Locked: {self.locked})"


