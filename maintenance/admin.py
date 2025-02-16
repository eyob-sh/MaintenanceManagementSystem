from django.contrib import admin
from .models import Branch, Department, Role, UserProfile
# Register your models here.
admin.site.register(Branch)
admin.site.register(Department)
admin.site.register(Role)
admin.site.register(UserProfile)