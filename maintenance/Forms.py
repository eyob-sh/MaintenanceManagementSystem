from django import forms
from .models import Equipment, SparePart, Manufacturer, DecommissionedEquipment, MaintenanceTask ,MaintenanceRecord, WorkOrder, SparePartUsage, RestockSparePart,Branch,UserProfile, Task, TaskGroup, TaskCompletion


class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super(BranchForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['user', 'branch',  'role']

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = [
            'name',
            'equipment_type',
            'manufacturer',
            'model_number',
            'serial_number',
            'branch',
            'location',
            'installation_date',
            
            'last_maintenance_date',
            'next_maintenance_date',
            'status',
            'remark',
        ]
    def __init__(self, *args, **kwargs):
        super(EquipmentForm, self).__init__(*args, **kwargs)
        # Loop through the fields and add the 'form-control' class
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})  # Add the Bootstrap class
        
        if self.instance and self.instance.pk:  # Check if the form is for an existing instance
            self.fields['branch'].disabled = True  # Disable the field
            self.fields['branch'].widget.attrs['readonly'] = True  # Make it read-only
            
            


class SparePartForm(forms.ModelForm):
    class Meta:
        model = SparePart
        fields = [
            'name',
            'branch',
            'store',
            'quantity',
            'part_number',
            'price',
            'description',
            'last_restock_date',

        ]

    def __init__(self, *args, **kwargs):
        super(SparePartForm, self).__init__(*args, **kwargs)
        # Loop through the fields and add the 'form-control' class
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})  # Add the Bootstrap class
            
        if self.instance and self.instance.pk:  # Check if the form is for an existing instance
            self.fields['branch'].disabled = True  # Disable the field
            self.fields['branch'].widget.attrs['readonly'] = True  # Make it read-only
            self.fields['quantity'].widget.attrs['readonly'] = True
            self.fields['last_restock_date'].widget.attrs['readonly'] = True

class RestockSparePartForm(forms.ModelForm):
    class Meta:
        model = RestockSparePart
        fields = ['spare_part', 'quantity', 'attachment']

            
            
            

class ManufacturerForm(forms.ModelForm):
    class Meta:
        model = Manufacturer
        fields = [
            'name',
            'description',
            'site',
            'contact_email',
            'contact_phone_number',
            'address',
        ]

    def __init__(self, *args, **kwargs):
        super(ManufacturerForm, self).__init__(*args, **kwargs)
        
        # Add Bootstrap 'form-control' class to all fields
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

        # Make the 'site' field read-only if the form is for an existing instance
        if self.instance and self.instance.pk:  # Check if the form is for an existing instance
            self.fields['site'].disabled = True  # Disable the field
            self.fields['site'].widget.attrs['readonly'] = True  # Make it read-only
            
class DecommissionedEquipmentForm(forms.ModelForm):
    class Meta:
        model = DecommissionedEquipment
        fields = [
            'equipment',
            'decommission_reason',
            'decommission_date',
        ]

    def __init__(self, *args, **kwargs):
        super(DecommissionedEquipmentForm, self).__init__(*args, **kwargs)
        # Add Bootstrap 'form-control' class to all fields
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
            
# class MaintenanceTaskForm(forms.ModelForm):
#     class Meta:
#         model = MaintenanceTask
#         fields = [
#             'equipment_type',
#             # 'branch',
#             'description',
#         ]

#     def __init__(self, *args, **kwargs):
#         super(MaintenanceTaskForm, self).__init__(*args, **kwargs)
#         # Add Bootstrap 'form-control' class to all fields
#         for field in self.fields.values():
#             field.widget.attrs.update({'class': 'form-control'})


class MaintenanceTaskForm(forms.ModelForm):
    class Meta:
        model = MaintenanceTask
        fields = ['equipment_type', 'description']
        widgets = {
            'equipment_type': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class TaskGroupForm(forms.ModelForm):
    class Meta:
        model = TaskGroup
        fields = ['frequency']

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['description']
            
        
            
class MaintenanceRecordForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRecord
        fields = [
            'equipment',
            'assigned_technicians',
            'branch',
            'maintenance_task',
            'maintenance_type',
            'remark',
            'procedure',
            'problems',
            'status',
            'completed_tasks',
        ]
        widgets = {
            'assigned_technicians': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'remark': forms.Textarea(attrs={'rows': 3}),
            'procedure': forms.Textarea(attrs={'rows': 3}),
            'problems': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super(MaintenanceRecordForm, self).__init__(*args, **kwargs)
        # Add Bootstrap 'form-control' class to all fields
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
            
        if self.instance and self.instance.pk:  # Check if the form is for an existing instance
            self.fields['branch'].disabled = True  # Disable the field
            self.fields['branch'].widget.attrs['readonly'] = True  # Make it read-only
            # self.fields['maintenance_task'].disabled = True  # Disable the maintenance task field
            # self.fields['maintenance_task'].widget.attrs['readonly'] = True  # Make it read-only
class WorkOrderForm(forms.ModelForm):
    class Meta:
        model = WorkOrder
        fields = [
            'requester',
            'branch',
            'equipment',
            'description',
            'status',
        ]

    def __init__(self, *args, **kwargs):
        super(WorkOrderForm, self).__init__(*args, **kwargs)
        # Add Bootstrap 'form-control' class to all fields
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
            
        if self.instance and self.instance.pk:  # Check if the form is for an existing instance
            self.fields['branch'].disabled = True  # Disable the field
            self.fields['branch'].widget.attrs['readonly'] = True  # Make it read-only
            
            
            
class SparePartUsageForm(forms.ModelForm):
    class Meta:
        model = SparePartUsage
        fields = [
            'maintenance_record',
            'spare_part',
            'quantity_used',
        ]

    def __init__(self, *args, **kwargs):
        super(SparePartUsageForm, self).__init__(*args, **kwargs)
        # Add Bootstrap 'form-control' class to all fields
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
            

            
            







