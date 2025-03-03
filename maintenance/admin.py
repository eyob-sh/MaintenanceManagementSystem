from django.contrib import admin
from .models import  *
from .models import DecommissionedEquipment, MaintenanceTask ,MaintenanceRecord, WorkOrder, SparePartUsage, Notification, RestockSparePart, Task, TaskGroup

# Register your models here.
admin.site.register(Branch)
admin.site.register(UserProfile)
admin.site.register(Manufacturer)
admin.site.register(Equipment)
admin.site.register(SparePart)
admin.site.register(DecommissionedEquipment)
admin.site.register(MaintenanceTask)
admin.site.register(Task)
admin.site.register(TaskGroup)
admin.site.register(MaintenanceRecord)
admin.site.register(WorkOrder)
admin.site.register(SparePartUsage)
admin.site.register(Notification)
admin.site.register(RestockSparePart)