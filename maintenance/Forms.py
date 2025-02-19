from django import forms
from .models import Equipment, SparePart

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