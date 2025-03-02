from django.contrib import admin
from .models import  *
from .models import DecommissionedEquipment, MaintenanceType ,MaintenanceRecord, WorkOrder, SparePartUsage, Notification, RestockSparePart

# Register your models here.
admin.site.register(Branch)
admin.site.register(UserProfile)
admin.site.register(Manufacturer)
admin.site.register(Equipment)
admin.site.register(SparePart)
admin.site.register(DecommissionedEquipment)
admin.site.register(MaintenanceType)
admin.site.register(MaintenanceRecord)
admin.site.register(WorkOrder)
admin.site.register(SparePartUsage)
admin.site.register(Notification)
admin.site.register(RestockSparePart)