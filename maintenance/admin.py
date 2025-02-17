from django.contrib import admin
from .models import Branch, Department, Role, UserProfile, Manufacturer, Equipment
# Register your models here.
admin.site.register(Branch)
admin.site.register(Department)
admin.site.register(Role)
admin.site.register(UserProfile)
admin.site.register(Manufacturer)
admin.site.register(Equipment)