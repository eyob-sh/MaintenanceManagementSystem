from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http import Http404
from datetime import datetime
from .Forms import EquipmentForm, SparePartForm, MaintenanceRecordForm, ChemicalForm

from django.contrib.auth import authenticate, login, logout

from .models import *
# Create your views here.


DEPARTMENT_CHOICES = [
    ('MD', 'Maintenance Department'),
    ('CD', 'Chemicals Department'),
    
]

# Define choices for roles
ROLE_CHOICES = [
    ('MD manager', 'Maintenance Department Manager'),
    ('TEC', 'Technician'),
    ('MO', 'Maintenance Oversight'),
    ('CO', 'Chemical oversight'),
    ('CL', 'Client'),
    ('AD', 'Admin'),
    
]





def custom_404_view(request, exception):
    return render(request, '404.html', status=404)

def custom_403_view(request, exception):
    return render(request, '404.html', status=403)


def loginPage(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # try:
        #     user = user.objects.get(username = username)
        
        # except: 
        #     messages.error(request, 'user does not exist')


        user = authenticate(request, username = username, password = password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else: 
            messages.error(request, 'Incorrect Username or Password')
        
    context = {}
    return render(request, 'login_page.html', context)


def logoutUser(request):
    logout(request)
    return redirect('login')


def register(request):
    branches = Branch.objects.all
    return render (request, 'register_page.html', {'branches': branches})


def add_user(request):
    if request.method == 'POST':
        first_name = request.POST.get('firstName')
        last_name = request.POST.get('lastName')
        username = request.POST.get('Username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')  # Now this is a string
        department = request.POST.get('department')
        branch_id = request.POST.get('branch')

        # Create the User
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        # Create UserProfile
        user_profile = UserProfile(
            user=user,
            branch_id=branch_id,
            department=department,
            role=role  # Store the role as a string
        )
        user_profile.save()

        return redirect('dashboard')  # Redirect to a success page or user list

    # For GET requests, render the register page
    return render(request, 'register_page.html')


def add_branch_page(request):
    return render(request,'branch.html')

def add_branch(request):
    if request.method == 'POST':
        branch_name = request.POST.get('name')  # Get the branch name from the form
        if branch_name:
            Branch.objects.create(name=branch_name)  # Create a new Branch object
            messages.success(request, 'Branch added successfully')
    return render(request, 'branch.html')  # Render the form if GET request


def add_manufacturer_page(request):
        return render(request,'manufacturer.html')

def add_manufacturer(request):
    if request.method == 'POST':
        # Get form data from the POST request
        name = request.POST.get('name')
        description = request.POST.get('description')
        contact_email = request.POST.get('contact_email')
        contact_phone_number = request.POST.get('contact_phone_number')
        address = request.POST.get('address')

        # Validate required fields (e.g., name is required)
        if not name:
            messages.error(request, 'Manufacturer name is required.')
            return redirect('add_manufacturer')  # Redirect back to the form

        # Create and save the Manufacturer object
        try:
            Manufacturer.objects.create(
                name=name,
                description=description,
                contact_email=contact_email,
                contact_phone_number=contact_phone_number,
                address=address
            )
            messages.success(request, 'Manufacturer added successfully!')
            return redirect('manufacturer_list.html')  # Redirect to a success page or manufacturer list
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('manufacturer.html')  # Redirect back to the form on error

# For GET requests, render the form
    return render(request, 'manufacturer.html')


def equipment_list(request):
    equipments = Equipment.objects.all()  # Fetch all equipment
    context = {
        'title': 'Equipments',
        'item_list': equipments,
        'edit_url': 'edit_equipment',  # Assuming you have an edit view set up
    }
    return render(request, 'equipment_list.html', context)



def add_equipment_page(request):
    manufacturers = Manufacturer.objects.all()
    branches = Branch.objects.all()
    return render (request, 'equipment.html', {
                'manufacturers': manufacturers,
                'branches': branches,
            })


def add_equipment(request):
    # Fetch all manufacturers and branches
    manufacturers = Manufacturer.objects.all()
    branches = Branch.objects.all()
    
    if request.method == 'POST':
        # Get form data
        name = request.POST.get('name')
        equipment_type = request.POST.get('equipment_type')
        manufacturer_id = request.POST.get('manufacturer')
        model_number = request.POST.get('model_number')
        serial_number = request.POST.get('serial_number')
        branch_id = request.POST.get('branch')
        location = request.POST.get('location')
        installation_date = request.POST.get('installation_date')
        
        # Use .get() with a default value for maintenance intervals
        maintenance_interval_years = request.POST.get('maintenance_interval_years', '0')
        maintenance_interval_months = request.POST.get('maintenance_interval_months', '0')
        maintenance_interval_weeks = request.POST.get('maintenance_interval_weeks', '0')
        maintenance_interval_days = request.POST.get('maintenance_interval_days', '0')
        
        status = request.POST.get('status')
        remark = request.POST.get('remark')
        
        # Validate required fields
        if not name or not equipment_type or not manufacturer_id or not model_number or not serial_number or not branch_id or not location or not installation_date or not status:
            messages.error(request, 'Please fill out all required fields.')
            context = {
                'manufacturers': manufacturers,
                'branches': branches,
            }
            return render(request, 'equipment.html', context)

        try:
            # Convert dates from string to date objects
            installation_date = datetime.strptime(installation_date, '%Y-%m-%d').date()

            # Convert maintenance intervals to integers
            maintenance_interval_years = int(maintenance_interval_years)
            maintenance_interval_months = int(maintenance_interval_months)
            maintenance_interval_weeks = int(maintenance_interval_weeks)
            maintenance_interval_days = int(maintenance_interval_days)

            # Create and save the Equipment object
            Equipment.objects.create(
                name=name,
                equipment_type=equipment_type,
                manufacturer_id=manufacturer_id,
                model_number=model_number,
                serial_number=serial_number,
                branch_id=branch_id,
                location=location,
                installation_date=installation_date,
                maintenance_interval_years=maintenance_interval_years,
                maintenance_interval_months=maintenance_interval_months,
                maintenance_interval_weeks=maintenance_interval_weeks,
                maintenance_interval_days=maintenance_interval_days,
                status=status,
                remark=remark
            )
            messages.success(request, 'Equipment added successfully!')
            return redirect('equipment_list')  # Redirect to a success page or equipment list
        except ValueError as e:
            messages.error(request, f'Invalid date format: {str(e)}')
            context = {
                'manufacturers': manufacturers,
                'branches': branches,
            }
            return render(request, 'equipment.html', context)
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            context = {
                'manufacturers': manufacturers,
                'branches': branches,
            }
            return render(request, 'equipment.html', context)

    # For GET requests, render the form with manufacturers and branches
    context = {
        'manufacturers': manufacturers,
        'branches': branches,
    }
    return render(request, 'equipment.html', context)



def edit_equipment(request, id):
    equipment = get_object_or_404(Equipment, id=id)  # Fetch the equipment instance

    if request.method == 'POST':
        form = EquipmentForm(request.POST, instance=equipment)
        if form.is_valid():
            form.save()  # Save the changes to the database
            messages.success(request, 'Equipment changed successfully')


            return redirect('equipment_list')  # Redirect to the equipment list after saving
    else:
        form = EquipmentForm(instance=equipment)  # Pre-fill the form with the current data

    return render(request, 'edit_equipment.html', {'form': form, 'equipment': equipment})



def spare_part_list(request):
    spare_parts = SparePart.objects.all()  # Fetch all sparepart
    context = {
        'title': 'Spare Parts',
        'item_list': spare_parts,
        'edit_url': 'edit_spare_part',  # Assuming you have an edit view set up
    }
    return render(request, 'spare_part_list.html', context)

def add_spare_part_page(request):
    branches = Branch.objects.all()
    return render (request, 'add_spare_part.html', {
                'branches': branches,
            })

def add_spare_part(request):
    
    # Fetch all branches
    branches = Branch.objects.all()

    if request.method == 'POST':
        # Get form data
        name = request.POST.get('name')
        branch_id = request.POST.get('branch')
        store = request.POST.get('store')
        quantity = request.POST.get('quantity')
        part_number = request.POST.get('part_number')
        price = request.POST.get('price')
        description = request.POST.get('description')

        # Validate required fields
        if not name or not branch_id or not store or not quantity or not part_number or not price:
            messages.error(request, 'Please fill out all required fields.')
            context = {
                'branches': branches,
            }
            return render(request, 'add_spare_part.html', context)

        try:
            # Convert quantity and price to appropriate types
            quantity = int(quantity)
            price = float(price)

            # Check if the part number already exists for the selected branch
            if SparePart.objects.filter(part_number=part_number, branch_id=branch_id).exists():
                messages.error(request, 'A spare part with this part number already exists in the selected branch.')
                context = {
                    'branches': branches,
                }
                return render(request, 'add_spare_part.html', context)

            # Create and save the SparePart object
            SparePart.objects.create(
                name=name,
                branch_id=branch_id,
                store=store,
                quantity=quantity,
                part_number=part_number,
                price=price,
                description=description
            )
            messages.success(request, 'Spare part added successfully!')
            return redirect('spare_part_list')  # Redirect to a success page or spare part list
        except ValueError as e:
            messages.error(request, f'Invalid input: {str(e)}')
            context = {
                'branches': branches,
            }
            return render(request, 'add_spare_part.html', context)
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            context = {
                'branches': branches,
            }
            return render(request, 'add_spare_part.html', context)

    # For GET requests, render the form with branches
    context = {
        'branches': branches,
    }
    return render(request, 'add_spare_part.html', context)
    
def edit_spare_part(request, id):
    spare_part = get_object_or_404(SparePart, id=id)  # Fetch the spare part instance

    if request.method == 'POST':
        form = SparePartForm(request.POST, instance=spare_part)
        if form.is_valid():
            form.save()  # Save the changes to the database
            messages.success(request, 'Spare part updated successfully!')
            return redirect('spare_part_list')  # Redirect to the spare part list after saving
    else:
        form = SparePartForm(instance=spare_part)  # Pre-fill the form with the current data

    return render(request, 'edit_spare_part.html', {'form': form, 'spare_part': spare_part})


 
    
    
def add_chemical_page(request):
    branches = Branch.objects.all()  # Fetch all branches for the dropdown
    return render(request, 'add_chemical.html', {
        'branches': branches,
    })

def add_chemical(request):
    branches = Branch.objects.all()  # Fetch all branches

    if request.method == 'POST':
        # Get form data
        chemical_name = request.POST.get('chemical_name')
        cas_number = request.POST.get('cas_number')
        molecular_formula = request.POST.get('molecular_formula')
        manufacturer_supplier = request.POST.get('manufacturer_supplier')
        catalog_number = request.POST.get('catalog_number')
        batch_lot_number = request.POST.get('batch_lot_number')
        quantity_available = request.POST.get('quantity_available')
        unit_of_measurement = request.POST.get('unit_of_measurement')
        location_storage_area = request.POST.get('location_storage_area')
        date_of_entry = request.POST.get('date_of_entry')
        expiration_date = request.POST.get('expiration_date')
        reorder_level = request.POST.get('reorder_level')
        sds_link = request.POST.get('sds_link')
        hazard_classification = request.POST.get('hazard_classification')
        usage_log = request.POST.get('usage_log')
        branch_id = request.POST.get('branch')

        # Validate required fields
        if not chemical_name or not cas_number or not manufacturer_supplier or not quantity_available or not unit_of_measurement or not location_storage_area or not date_of_entry or not branch_id:
            messages.error(request, 'Please fill out all required fields.')
            context = {
                'branches': branches,
            }
            return render(request, 'add_chemical.html', context)

        try:
            # Convert quantity and reorder level to appropriate types
            quantity_available = float(quantity_available)
            reorder_level = float(reorder_level)

            # Create and save the Chemical object
            Chemical.objects.create(
                chemical_name=chemical_name,
                cas_number=cas_number,
                molecular_formula=molecular_formula,
                manufacturer_supplier=manufacturer_supplier,
                catalog_number=catalog_number,
                batch_lot_number=batch_lot_number,
                quantity_available=quantity_available,
                unit_of_measurement=unit_of_measurement,
                location_storage_area=location_storage_area,
                date_of_entry=date_of_entry,
                expiration_date=expiration_date,
                reorder_level=reorder_level,
                sds_link=sds_link,
                hazard_classification=hazard_classification,
                usage_log=usage_log,
                branch_id=branch_id,
            )
            messages.success(request, 'Chemical added successfully!')
            return redirect('chemical_list')  # Redirect to the chemical list
        except ValueError as e:
            messages.error(request, f'Invalid input: {str(e)}')
            context = {
                'branches': branches,
            }
            return render(request, 'add_chemical.html', context)
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            context = {
                'branches': branches,
            }
            return render(request, 'add_chemical.html', context)

    # For GET requests, render the form with branches
    context = {
        'branches': branches,
    }
    return render(request, 'add_chemical.html', context)

def chemical_list(request):
    chemicals = Chemical.objects.all()  # Fetch all chemicals
    context = {
        'title': 'Chemical List',
        'item_list': chemicals,
        'edit_url': 'edit_chemical',  # URL name for editing chemicals
    }
    return render(request, 'chemical_list.html', context)


def edit_chemical(request, id):
    chemical = get_object_or_404(Chemical, id=id)  # Fetch the chemical instance

    if request.method == 'POST':
        form = ChemicalForm(request.POST, instance=chemical)
        if form.is_valid():
            form.save()  # Save the changes to the database
            messages.success(request, 'Chemical updated successfully!')
            return redirect('chemical_list')  # Redirect to the chemical list
    else:
        form = ChemicalForm(instance=chemical)  # Pre-fill the form with the current data

    return render(request, 'edit_chemical.html', {'form': form, 'chemical': chemical})
    
    
def add_maintenance_page(request):
    context = {
        'equipments': Equipment.objects.all(),
        'technicians': User.objects.filter(is_staff=True),  # Filter technicians
        'branches': Branch.objects.all(),
        'maintenance_types': MaintenanceType.objects.all(),
        'work_orders': WorkOrder.objects.all(),
        'spare_parts': SparePart.objects.all(),
    }
    return render(request, 'add_maintenance.html', context)

def add_maintenance(request):
    context = {
        'equipments': Equipment.objects.all(),
        'technicians': User.objects.filter(is_staff=True),
        'branches': Branch.objects.all(),
        'maintenance_types': MaintenanceType.objects.all(),
        'work_orders': WorkOrder.objects.all(),
        'spare_parts': SparePart.objects.all(),
    }

    if request.method == 'POST':
        # Get form data
        equipment_id = request.POST.get('equipment')
        assigned_technicians = request.POST.getlist('assigned_technicians')
        branch_id = request.POST.get('branch')
        maintenance_type_id = request.POST.get('maintenance_type')
        maintenance_for = request.POST.get('maintenance_for')
        work_order_id = request.POST.get('work_order')
        spare_parts = request.POST.getlist('spare_parts')
        remark = request.POST.get('remark')
        procedure = request.POST.get('procedure')
        problems = request.POST.get('problems')
        status = request.POST.get('status')

        # Validate required fields
        if not equipment_id or not assigned_technicians or not branch_id or not maintenance_type_id or not maintenance_for or not status:
            messages.error(request, 'Please fill out all required fields.')
            return render(request, 'add_maintenance.html', context)

        try:
            # Create and save the MaintenanceRecord object
            maintenance = MaintenanceRecord.objects.create(
                equipment_id=equipment_id,
                branch_id=branch_id,
                maintenance_type_id=maintenance_type_id,
                maintenance_for=maintenance_for,
                work_order_id=work_order_id,
                remark=remark,
                procedure=procedure,
                problems=problems,
                status=status,
            )
            maintenance.assigned_technicians.set(assigned_technicians)
            maintenance.spare_parts.set(spare_parts)

            messages.success(request, 'Maintenance record added successfully!')
            return redirect('maintenance_list')  # Redirect to the maintenance list
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return render(request, 'add_maintenance.html', context)

    # For GET requests, render the form with context
    return render(request, 'add_maintenance.html', context)
    
    
    

def maintenance_list(request):
    maintenance_records = MaintenanceRecord.objects.all()  # Fetch all maintenance records
    context = {
        'title': 'Maintenance List',
        'item_list': maintenance_records,
        'edit_url': 'edit_maintenance',  # URL name for editing maintenance records
    }
    return render(request, 'maintenance_list.html', context)
    
def edit_maintenance(request, id):
    maintenance = get_object_or_404(MaintenanceRecord, id=id)  # Fetch the maintenance record instance

    if request.method == 'POST':
        form = MaintenanceRecordForm(request.POST, instance=maintenance)
        if form.is_valid():
            form.save()  # Save the changes to the database
            messages.success(request, 'Maintenance record updated successfully!')
            return redirect('maintenance_list')  # Redirect to the maintenance list
    else:
        form = MaintenanceRecordForm(instance=maintenance)  # Pre-fill the form with the current data

    return render(request, 'edit_maintenance.html', {'form': form, 'maintenance': maintenance})





@login_required()
def dashboard(request):
    return render(request, 'dashboard.html')

@login_required()
def equipment(request):
    return render(request, 'equipment.html')