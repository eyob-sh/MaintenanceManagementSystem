from django import forms
from .models import Chemical, RestockChemical


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
        if self.instance and self.instance.pk:  # Check if the form is for an existing instance
            self.fields['quantity_available'].widget.attrs['readonly'] = True  # Make it read-only

class RestockChemicalForm(forms.ModelForm):
    class Meta:
        model = RestockChemical
        fields = ['chemical', 'quantity', 'attachment']
            