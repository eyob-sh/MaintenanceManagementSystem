# resources.py
from import_export import resources, fields
from .models import Equipment, Branch, Manufacturer

class EquipmentResource(resources.ModelResource):
    # Add fields for related models (branch and manufacturer)
    branch = fields.Field(attribute='branch', column_name='Branch')
    manufacturer = fields.Field(attribute='manufacturer', column_name='Manufacturer')

    class Meta:
        model = Equipment
        fields = ('name', 'equipment_type', 'branch', 'manufacturer', 'serial_number', 'location', 'installation_date', 'status')
        export_order = fields  # Optional: Define the order of exported fields

    def dehydrate_branch(self, equipment):
        """
        Customize the branch field to display the branch name instead of ID.
        """
        return equipment.branch.name if equipment.branch else ''

    def dehydrate_manufacturer(self, equipment):
        """
        Customize the manufacturer field to display the manufacturer name instead of ID.
        """
        return equipment.manufacturer.name if equipment.manufacturer else ''

    def before_import_row(self, row, **kwargs):
        """
        Look up Branch and Manufacturer by name before importing the row.
        """
        # Look up Branch by name
        branch_name = row.get('Branch')
        if branch_name:
            branch, created = Branch.objects.get_or_create(name=branch_name)
            row['branch'] = branch.id

        # Look up Manufacturer by name
        manufacturer_name = row.get('Manufacturer')
        if manufacturer_name:
            manufacturer, created = Manufacturer.objects.get_or_create(name=manufacturer_name)
            row['manufacturer'] = manufacturer.id