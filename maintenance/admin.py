from django.contrib import admin
from .models import  *
from .models import( DecommissionedEquipment, 
                    MaintenanceTask ,
                    MaintenanceRecord,
                      WorkOrder, 
                      SparePartUsage, 
                      Notification, 
                      RestockSparePart, 
                      Task, 
                      TaskGroup,
                      TaskCompletion, 
                      SchedulerLock, 
                      SparePartTransaction, 
                      SparePartRequest,
                      TechnicianSparePart)

# Register your models here.
admin.site.register(Branch)
admin.site.register(UserProfile)
admin.site.register(Manufacturer)
# admin.site.register(Equipment)
admin.site.register(SparePart)
admin.site.register(DecommissionedEquipment)
admin.site.register(MaintenanceTask)
admin.site.register(Task)
admin.site.register(TaskGroup)
admin.site.register(TaskCompletion)
admin.site.register(MaintenanceRecord)
admin.site.register(WorkOrder)
admin.site.register(SparePartUsage)
admin.site.register(Notification)
admin.site.register(RestockSparePart)
admin.site.register(SchedulerLock)
admin.site.register(SparePartRequest)
admin.site.register(SparePartTransaction)
admin.site.register(TechnicianSparePart)



@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'equipment_type', 'manufacturer', 'model_number', 'status', 'created_at')  # Add created_at here