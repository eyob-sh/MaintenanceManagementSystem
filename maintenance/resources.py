from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import Equipment, Branch, Manufacturer, MaintenanceTask

class EquipmentResource(resources.ModelResource):
    # Use ForeignKeyWidget for branch and manufacturer
    branch = fields.Field(
        attribute='branch',
        column_name='Branch',  # Ensure this matches the column name in the import file
        widget=ForeignKeyWidget(Branch, 'name')  # Lookup by 'name' field
    )
    manufacturer = fields.Field(
        attribute='manufacturer',
        column_name='Manufacturer',  # Ensure this matches the column name in the import file
        widget=ForeignKeyWidget(Manufacturer, 'name')  # Lookup by 'name' field
    )
    equipment_type = fields.Field(
        attribute='equipment_type',
        column_name='Equipment Type'  # Ensure this matches the column name in the import file
    )
    model_number = fields.Field(
        attribute='model_number',
        column_name='Model Number'  # Ensure this matches the column name in the import file
    )

    class Meta:
        model = Equipment
        fields = (
            'name', 'equipment_type', 'branch', 'manufacturer', 'model_number', 'serial_number', 'location',
            'installation_date', 'status'
        )
        # Remove import_id_fields to avoid looking for 'id'
        import_id_fields = ()  # Explicitly set to an empty tuple

    def dehydrate_branch(self, equipment):
        """
        Customize the branch field to display the branch name during export.
        """
        return equipment.branch.name if equipment.branch else ''

    def dehydrate_manufacturer(self, equipment):
        """
        Customize the manufacturer field to display the manufacturer name during export.
        """
        return equipment.manufacturer.name if equipment.manufacturer else ''

    def before_import_row(self, row, **kwargs):
        """
        Preprocess each row before importing:
        - Validate equipment_type against MaintenanceTask.
        - Append errors if any validation fails.
        """
        # Validate equipment_type against MaintenanceTask
        equipment_type = row.get('Equipment Type')
        if equipment_type:
            valid_equipment_types = MaintenanceTask.objects.values_list('equipment_type', flat=True).distinct()
            if equipment_type not in valid_equipment_types:
                row_result = kwargs.get('row_result')
                if row_result:
                    row_result.errors.append(
                        (f"Equipment Type '{equipment_type}' is not valid.",)
                    )

    def import_obj(self, obj, data, dry_run):
        """
        Skip the 'id' field during import.
        """
        if 'id' in data:
            del data['id']
        super().import_obj(obj, data, dry_run)