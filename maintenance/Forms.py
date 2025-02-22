from django import forms
from .models import Equipment, SparePart, Manufacturer, DecommissionedEquipment, MaintenanceType ,MaintenanceRecord, WorkOrder, SparePartUsage, Chemical, Branch, UserProfile
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
            'maintenance_interval_years',
            'maintenance_interval_months',
            'maintenance_interval_weeks',
            'maintenance_interval_days',
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
        ]

    def __init__(self, *args, **kwargs):
        super(SparePartForm, self).__init__(*args, **kwargs)
        # Loop through the fields and add the 'form-control' class
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})  # Add the Bootstrap class
            

class ManufacturerForm(forms.ModelForm):
    class Meta:
        model = Manufacturer
        fields = [
            'name',
            'description',
            'contact_email',
            'contact_phone_number',
            'address',
        ]

    def __init__(self, *args, **kwargs):
        super(ManufacturerForm, self).__init__(*args, **kwargs)
        # Add Bootstrap 'form-control' class to all fields
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
            
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
            
class MaintenanceTypeForm(forms.ModelForm):
    class Meta:
        model = MaintenanceType
        fields = [
            'maintenance_type',
            'description',
        ]

    def __init__(self, *args, **kwargs):
        super(MaintenanceTypeForm, self).__init__(*args, **kwargs)
        # Add Bootstrap 'form-control' class to all fields
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
            
class MaintenanceRecordForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRecord
        fields = [
            'equipment',
            'assigned_technicians',
            'branch',
            'maintenance_type',
            'remark',
            'procedure',
            'problems',
            'status',
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
            
class ChemicalForm(forms.ModelForm):
    class Meta:
        model = Chemical
        fields = [
            'chemical_name',
            'cas_number',
            'molecular_formula',
            'manufacturer_supplier',
            'catalog_number',
            'batch_lot_number',
            'quantity_available',
            'unit_of_measurement',
            'location_storage_area',
            'date_of_entry',
            'expiration_date',
            'reorder_level',
            'sds_link',
            'hazard_classification',
            'usage_log',
        ]
        widgets = {
            'date_of_entry': forms.DateInput(attrs={'type': 'date'}),
            'expiration_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super(ChemicalForm, self).__init__(*args, **kwargs)
        # Add Bootstrap 'form-control' class to all fields
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
            
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
        fields = ['user', 'branch', 'department', 'role']

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})






