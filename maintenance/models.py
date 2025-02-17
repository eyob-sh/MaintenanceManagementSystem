from django.db import models
from django.contrib.auth.models import User

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
    Location = models.CharField(max_length=50)
    Installation_date = models.DateField()
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
    