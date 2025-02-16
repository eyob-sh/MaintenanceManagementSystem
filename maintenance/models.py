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