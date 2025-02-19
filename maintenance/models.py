from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone



# Create your models here.
class Branch(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Department(models.Model):
    name = models.CharField(max_length=100)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='departments')

    # Permissions specific to the department
    permissions = models.JSONField(default=dict)  # Store permissions as a JSON object

    def __str__(self):
        return self.name

class Role(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='roles')

    # Permissions specific to the role
    permissions = models.JSONField(default=dict)  # Store permissions as a JSON object

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.user.username

    def get_permissions(self):
        # Combine permissions from role and department
        role_permissions = self.role.permissions if self.role else {}
        department_permissions = self.department.permissions if self.department else {}
        combined_permissions = {**department_permissions, **role_permissions}
        return combined_permissions
    

class MaintenanceType(models.Model):

    maintenance_type = models.CharField(
        help_text="Enter a type of maintenance "
                  "(e.g., 'Software Installation').",
        max_length=255,
        unique=True,
    )

    description = models.TextField(
        blank=True,
        help_text='Enter a description of the maintenance type.',
    )

    class Meta:
        ordering = ['maintenance_type']

    def __str__(self):
        return self.maintenance_type


class Manufacturer(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
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
        ('decommissioned', 'Decommissioned'),
        
    ]

   

   

    name = models.CharField(max_length=100)
    equipment_type = models.CharField(max_length=50)  # To specify if it's a machine, tool, etc.
    manufacturer = models.ForeignKey('Manufacturer', on_delete=models.PROTECT)
    model_number = models.CharField(max_length=50)
    serial_number = models.CharField(max_length=50, unique=True)
    branch = models.ForeignKey('Branch', on_delete=models.PROTECT)
    location = models.CharField(max_length=50)
    installation_date = models.DateField()
    maintenance_interval_years = models.PositiveIntegerField(default=0)
    maintenance_interval_months = models.PositiveIntegerField(default=0)
    maintenance_interval_weeks = models.PositiveIntegerField(default=0)
    maintenance_interval_days = models.PositiveIntegerField(default=0)
    last_maintenance_date = models.DateField(null=True, blank=True)
    next_maintenance_date = models.DateField(null=True, blank=True, )  # New field
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='operational')
    remark = models.TextField(blank=True)
    
    


    def __str__(self):
        return f"{self.name} ({self.equipment_type} -- {self.serial_number}) "
    

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
    
    class Meta:
        unique_together = ('part_number', 'branch')

    def __str__(self):
        return f"{self.name} ({self.quantity} left) - {self.store}"
    

    
class WorkOrder(models.Model):
    requester = models.ForeignKey(
        User,  # Use the built-in User model
        on_delete=models.CASCADE,
        related_name='work_orders',
        help_text='The user requesting the maintenance.',
    )
    branch = models.ForeignKey('Branch', on_delete=models.PROTECT)

    equipment = models.ForeignKey(
        'Equipment',
        on_delete=models.PROTECT,
        help_text='Select the equipment that needs maintenance.',
    )
    description = models.TextField(
        help_text='Describe the maintenance needed.',
    )
    status = models.CharField(
        choices=[
            ('Pending', 'Pending'),
            ('In Progress', 'In Progress'),
            ('Completed', 'Completed'),
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
    ('Complete', 'Complete'),
    ('In Progress', 'In Progress'),
    ('Failed', 'Failed'),
]
    
    MAINTENANCE_FOR = [
    ('Scheduled_Maintenance', 'Scheduled_Maintenance'),
    ('Work Order' ,'Work Order')
]

    
    equipment = models.ForeignKey(
        'Equipment',
        help_text='Select/Create an equipment.',
        on_delete=models.PROTECT,
    )
    
    

    assigned_technicians = models.ManyToManyField(
        User,

        help_text='The users who are assigned to perform the maintenace.',
        related_name='maintenance_records',)
    
    branch = models.ForeignKey(
        'Branch',
        on_delete=models.PROTECT,
        help_text='Select the branch for this user.',
    )
    

    maintenance_type = models.ForeignKey(
        'MaintenanceType',
        help_text='Select/Create a maintenance type.',
        on_delete=models.PROTECT,
    )
    
    maintenance_for = models.CharField(
        max_length=30,
        default='Scheduled_Maintenance',
        choices=MAINTENANCE_FOR,
        help_text='Select the type of maintenance.',
    )

    work_order = models.ForeignKey(
        'WorkOrder',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        help_text='Select a work order if applicable.',
    )
    
    spare_parts = models.ManyToManyField('SparePart', through='SparePartUsage')

   

    remark = models.TextField(
        blank=True,
        help_text='Enter remarks for the maintenance performed.',
        null=True,
    )

    procedure = models.TextField(
        blank=True,
        help_text='Enter details of how the maintenance was performed.',
        null=True,
    )

    problems = models.TextField(
        blank=True,
        help_text='Describe problems that arose during maintenance.',
        null=True,
    )

    

    

    status = models.CharField(
        choices = STATUS_CHOICES,
        default='Not Started',
        help_text='What is the current status of the system maintenance?',
        max_length=15,
    )
    
    
    datetime = models.DateTimeField(auto_now_add=True
    )


    def __str__(self):
        return '{} - {} ({})'.format(
            self.equipment, self.maintenance_type, self.datetime.date())
        
    
class SparePartUsage(models.Model):
    maintenance_record = models.ForeignKey(MaintenanceRecord, on_delete=models.CASCADE)
    spare_part = models.ForeignKey(SparePart, on_delete=models.CASCADE)
    quantity_used = models.IntegerField()  # Quantity of the spare part used
    

class DecommissionedEquipment(models.Model):
    equipment = models.OneToOneField('Equipment', on_delete=models.CASCADE)
    decommission_reason = models.TextField(blank=True, null=True)
    decommission_date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.equipment.name} - Decommissioned on {self.decommission_date}"
    


class Chemical(models.Model):
    
    UNIT_CHOICES = [
        ('L', 'Liter (L)'),
        ('mL', 'Milliliter (mL)'),
        ('kg', 'Kilogram (kg)'),
        ('g', 'Gram (g)'),
        ('mg', 'Milligram (mg)'),
        ('mol', 'Mole (mol)'),
        ('mmol', 'Millimole (mmol)'),
        ('m³', 'Cubic Meter (m³)'),
        ('cm³', 'Cubic Centimeter (cm³)'),
        ('gal', 'Gallon (gal)'),
        ('lb', 'Pound (lb)'),
        ('oz', 'Ounce (oz)'),
        ('piece', 'Piece'),
        ('unit', 'Unit'),
        ('box', 'Box'),
        ('bottle', 'Bottle'),
        ('pack', 'Pack'),
        ('bag', 'Bag'),
        ('can', 'Can'),
        ('tube', 'Tube'),
        ('carton', 'Carton'),
        ('pallet', 'Pallet'),
    ]
    
    # Chemical Information
    chemical_name = models.CharField(
        max_length=255,
        help_text="Enter the IUPAC or common name of the chemical.",
    )
    cas_number = models.CharField(
        max_length=50,
        unique=True,
        help_text="Enter the Chemical Abstracts Service (CAS) registry number.",
    )
    molecular_formula = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Enter the molecular formula of the chemical (if applicable).",
    )

    # Manufacturer/Supplier Information
    manufacturer_supplier = models.CharField(
        max_length=255,
        help_text="Enter the manufacturer or supplier name (brand/vendor).",
    )
    catalog_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Enter the catalog number (if sourced externally).",
    )
    batch_lot_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Enter the batch or lot number for tracking specific batches.",
    )

    # Quantity and Storage
    quantity_available = models.FloatField(
        validators=[MinValueValidator(0)],
        help_text="Enter the quantity available in stock (e.g., mL, L, g, kg).",
    )
    unit_of_measurement = models.CharField(
        max_length=50,
        choices=UNIT_CHOICES,
        help_text="Select the unit of measurement"
    )
    location_storage_area = models.CharField(
        max_length=255,
        help_text="Enter the location or storage area (e.g., Shelf A, Lab 2, Flammable Cabinet).",
    )
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)

    # Dates
    date_of_entry = models.DateField(
        default=timezone.now,
        help_text="Enter the date when the chemical was added to inventory.",
    )
    expiration_date = models.DateField(
        blank=True,
        null=True,
        help_text="Enter the expiration date to track usability.",
    )

    # Reorder and Safety
    reorder_level = models.FloatField(
        validators=[MinValueValidator(0)],
        help_text="Enter the reorder level threshold to notify restocking needs.",
    )
    sds_link = models.URLField(
        blank=True,
        null=True,
        help_text="Enter the Safety Data Sheet (SDS) link for safety reference.",
    )
    hazard_classification = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Enter the hazard classification (e.g., GHS labeling, NFPA).",
    )

    # Usage Log (Optional, can be handled separately)
    usage_log = models.TextField(
        blank=True,
        null=True,
        help_text="Enter the history of usage and users handling the chemical.",
    )

    def __str__(self):
        return f"{self.chemical_name} ({self.cas_number})"

    class Meta:
        verbose_name = "Chemical"
        verbose_name_plural = "Chemicals"
        ordering = ['chemical_name']
    