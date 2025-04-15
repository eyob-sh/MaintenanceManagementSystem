from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import Equipment, Branch, Manufacturer, MaintenanceTask

# Custom Widget for Manufacturer with Branch Context
class ManufacturerBranchWidget(ForeignKeyWidget):
    """
    Custom widget that looks up manufacturers by both name and branch.
    Creates new manufacturers if they don't exist for the branch.
    """
    def __init__(self):
        # Initialize with Manufacturer model and 'name' field
        super().__init__(Manufacturer, 'name')
    
    def get_queryset(self, value, row, *args, **kwargs):
        if not value:  # No manufacturer name provided
            return Manufacturer.objects.none()
            
        branch_name = row.get('Branch')
        if not branch_name:  # No branch specified
            return Manufacturer.objects.none()
            
        return Manufacturer.objects.filter(
            name=value,
            site__name=branch_name
        )

    def clean(self, value, row=None, *args, **kwargs):
        if not value:  # Empty manufacturer field
            return None
            
        try:
            branch_name = row.get('Branch')
            if not branch_name:
                raise ValueError("Manufacturer requires branch information")
                
            # Try to get existing manufacturer
            return Manufacturer.objects.get(
                name=value,
                site__name=branch_name
            )
        except Manufacturer.DoesNotExist:
            # Create new manufacturer for this branch
            branch = Branch.objects.get(name=branch_name)
            return Manufacturer.objects.create(
                name=value,
                site=branch
            )
        except Manufacturer.MultipleObjectsReturned:
            # Fallback if unique_together fails
            return Manufacturer.objects.filter(
                name=value,
                site__name=branch_name
            ).first()

# Main Equipment Resource
class EquipmentResource(resources.ModelResource):
    branch = fields.Field(
        attribute='branch',
        column_name='Branch',
        widget=ForeignKeyWidget(Branch, 'name')
    )
    
    manufacturer = fields.Field(
        attribute='manufacturer',
        column_name='Manufacturer',
        widget=ManufacturerBranchWidget()  # Using our custom widget
    )
    
    equipment_type = fields.Field(
        attribute='equipment_type',
        column_name='Equipment Type'
    )
    
    model_number = fields.Field(
        attribute='model_number',
        column_name='Model Number'
    )

    class Meta:
        model = Equipment
        fields = (
            'name', 'equipment_type', 'branch', 'manufacturer', 
            'model_number', 'serial_number', 'location',
            'installation_date', 'status'
        )
        import_id_fields = ()

    def dehydrate_branch(self, equipment):
        """Format branch name for export"""
        return equipment.branch.name if equipment.branch else ''

    def dehydrate_manufacturer(self, equipment):
        """Format manufacturer name for export"""
        return equipment.manufacturer.name if equipment.manufacturer else ''

    def before_import_row(self, row, **kwargs):
        """
        Validate equipment type against allowed types.
        This runs after manufacturer/branch are resolved.
        """
        row_result = kwargs.get('row_result')  # Get row_result from kwargs
    
        equipment_type = row.get('Equipment Type')
        if equipment_type:
            valid_types = MaintenanceTask.objects.values_list(
                'equipment_type', 
                flat=True
            ).distinct()
            if equipment_type not in valid_types and row_result:
                row_result.errors.append(
                    (f"Invalid equipment type: {equipment_type}",)
                )
        # Enhanced branch validation
        branch_name = row.get('Branch')
        user_branch = kwargs.get('user_branch')
        if branch_name and user_branch and branch_name != user_branch.name:
            if row_result:  # Only add error if row_result exists
                row_result.errors.append(
                    (f"Cannot import equipment for branch '{branch_name}'. "
                     f"You can only import for your branch ({user_branch.name}).",)
                )
                return False  # Mark row as invalid
            else:
                # For cases where row_result doesn't exist (shouldn't happen in normal flow)
                raise ValueError(
                    f"Cannot import equipment for branch '{branch_name}'. "
                    f"You can only import for your branch ({user_branch.name})."
                )
        
        return True
    def import_obj(self, obj, data, dry_run):
        """Skip ID field during import"""
        if 'id' in data:
            del data['id']
        super().import_obj(obj, data, dry_run)