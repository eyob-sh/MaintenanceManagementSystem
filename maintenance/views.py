from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.http import Http404
from datetime import datetime
from .Forms import EquipmentForm, SparePartForm, MaintenanceRecordForm, ChemicalForm, ManufacturerForm, WorkOrderForm, SparePartUsageForm, DecommissionedEquipmentForm, MaintenanceTypeForm, BranchForm, UserProfileForm

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


# def register(request):
#     branches = Branch.objects.all
#     return render (request, 'register_page.html', {'branches': branches})


# def add_user(request):
#     if request.method == 'POST':
#         first_name = request.POST.get('firstName')
#         last_name = request.POST.get('lastName')
#         username = request.POST.get('Username')
#         email = request.POST.get('email')
#         password = request.POST.get('password')
#         role = request.POST.get('role')  # Now this is a string
#         department = request.POST.get('department')
#         branch_id = request.POST.get('branch')

#         # Create the User
#         user = User.objects.create_user(
#             username=username,
#             email=email,
#             password=password,
#             first_name=first_name,
#             last_name=last_name
#         )

#         # Create UserProfile
#         user_profile = UserProfile(
#             user=user,
#             branch_id=branch_id,
#             department=department,
#             role=role  # Store the role as a string
#         )
#         user_profile.save()

#         return redirect('')  # Redirect to a success page or user list

#     # For GET requests, render the register page
#     return render(request, 'register_page.html')


# def add_branch_page(request):
#     return render(request,'branch.html')

# def add_branch(request):
#     if request.method == 'POST':
#         branch_name = request.POST.get('name')  # Get the branch name from the form
#         if branch_name:
#             Branch.objects.create(name=branch_name)  # Create a new Branch object
#             messages.success(request, 'Branch added successfully')
#     return render(request, 'branch.html')  # Render the form if GET request

@login_required
def my_profile(request):
    # Get the current user's profile
    user_profile = UserProfile.objects.get(user=request.user)
    
    if request.method == 'POST':
        # Handle email update
        new_email = request.POST.get('email')
        if new_email and new_email != request.user.email:
            # Update the user's email
            request.user.email = new_email
            request.user.save()
            messages.success(request, 'Email updated successfully!')

        # Handle password update
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmPassword')
        if password and confirm_password:
            if password == confirm_password:
                # Update the user's password
                request.user.password = make_password(password)
                request.user.save()
                messages.success(request, 'Password updated successfully!')
            else:
                messages.error(request, 'Passwords do not match!')
                return redirect('my_profile')
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('my_profile')
    
    return render(request, 'my_profile.html', {
        'user_profile': user_profile,
    })


def manufacturer_list(request):
    manufacturers = Manufacturer.objects.all()
    context = {
        'title': 'Manufacturers',
        'item_list': manufacturers,
        'edit_url': 'edit_manufacturer',
    }
    return render(request, 'manufacturer_list.html', context)

def add_manufacturer_page(request):
    return render(request, 'add_manufacturer.html')

def add_manufacturer(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        contact_email = request.POST.get('contact_email')
        contact_phone_number = request.POST.get('contact_phone_number')
        address = request.POST.get('address')

        if not name or not contact_email:
            messages.error(request, 'Please fill out all required fields.')
            return render(request, 'add_manufacturer.html')

        try:
            Manufacturer.objects.create(
                name=name,
                description=description,
                contact_email=contact_email,
                contact_phone_number=contact_phone_number,
                address=address
            )
            messages.success(request, 'Manufacturer added successfully!')
            return redirect('manufacturer_list')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return render(request, 'add_manufacturer.html')

    return render(request, 'add_manufacturer.html')

def edit_manufacturer(request, id):
    manufacturer = get_object_or_404(Manufacturer, id=id)

    if request.method == 'POST':
        form = ManufacturerForm(request.POST, instance=manufacturer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Manufacturer updated successfully!')
            return redirect('manufacturer_list')
    else:
        form = ManufacturerForm(instance=manufacturer)

    return render(request, 'edit_manufacturer.html', {'form': form, 'manufacturer': manufacturer})

#----------------------------------------------------------------------------------

def work_order_list(request):
    work_orders = WorkOrder.objects.all()
    context = {
        'title': 'Work Orders',
        'item_list': work_orders,
        'edit_url': 'edit_work_order',
    }
    return render(request, 'work_order_list.html', context)

def add_work_order_page(request):
    equipments = Equipment.objects.all()
    users = User.objects.all()
    branches = Branch.objects.all()
    return render(request, 'add_work_order.html', {
        'equipments': equipments,
        'users': users,
        'branches': branches,
    })

def add_work_order(request):
    if request.method == 'POST':
        requester_id = request.POST.get('requester')
        branch_id = request.POST.get('branch')
        equipment_id = request.POST.get('equipment')
        description = request.POST.get('description')
        status = request.POST.get('status')

        if not requester_id or not branch_id or not equipment_id or not description or not status:
            messages.error(request, 'Please fill out all required fields.')
            return redirect('add_work_order_page')

        try:
            WorkOrder.objects.create(
                requester_id=requester_id,
                branch_id=branch_id,
                equipment_id=equipment_id,
                description=description,
                status=status
            )
            messages.success(request, 'Work Order added successfully!')
            return redirect('work_order_list')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('add_work_order_page')

    return redirect('add_work_order_page')



def edit_work_order(request, id):
    work_order = get_object_or_404(WorkOrder, id=id)

    if request.method == 'POST':
        form = WorkOrderForm(request.POST, instance=work_order)
        if form.is_valid():
            form.save()
            messages.success(request, 'Work Order updated successfully!')
            return redirect('work_order_list')
    else:
        form = WorkOrderForm(instance=work_order)

    return render(request, 'edit_work_order.html', {'form': form, 'work_order': work_order})

#---------------------------------------------------------------------------------------

def spare_part_usage_list(request):
    spare_part_usages = SparePartUsage.objects.all()
    context = {
        'title': 'Spare Part Usages',
        'item_list': spare_part_usages,
        'edit_url': 'edit_spare_part_usage',
    }
    return render(request, 'spare_part_usage_list.html', context)

def add_spare_part_usage_page(request):
    maintenance_records = MaintenanceRecord.objects.all()
    spare_parts = SparePart.objects.all()
    return render(request, 'add_spare_part_usage.html', {
        'maintenance_records': maintenance_records,
        'spare_parts': spare_parts,
    })

def add_spare_part_usage(request):
    if request.method == 'POST':
        maintenance_record_id = request.POST.get('maintenance_record')
        spare_part_id = request.POST.get('spare_part')
        quantity_used = request.POST.get('quantity_used')

        if not maintenance_record_id or not spare_part_id or not quantity_used:
            messages.error(request, 'Please fill out all required fields.')
            return redirect('add_spare_part_usage_page')

        try:
            SparePartUsage.objects.create(
                maintenance_record_id=maintenance_record_id,
                spare_part_id=spare_part_id,
                quantity_used=quantity_used
            )
            messages.success(request, 'Spare Part Usage added successfully!')
            return redirect('spare_part_usage_list')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('add_spare_part_usage_page')

    return redirect('add_spare_part_usage_page')

def edit_spare_part_usage(request, id):
    spare_part_usage = get_object_or_404(SparePartUsage, id=id)

    if request.method == 'POST':
        form = SparePartUsageForm(request.POST, instance=spare_part_usage)
        if form.is_valid():
            form.save()
            messages.success(request, 'Spare Part Usage updated successfully!')
            return redirect('spare_part_usage_list')
    else:
        form = SparePartUsageForm(instance=spare_part_usage)

    return render(request, 'edit_spare_part_usage.html', {'form': form, 'spare_part_usage': spare_part_usage})

#------------------------------------------------------------------------------------
def decommissioned_equipment_list(request):
    decommissioned_equipments = DecommissionedEquipment.objects.all()
    context = {
        'title': 'Decommissioned Equipments',
        'item_list': decommissioned_equipments,
        'edit_url': 'edit_decommissioned_equipment',
    }
    return render(request, 'decommissioned_equipment_list.html', context)

def add_decommissioned_equipment_page(request):
    equipments = Equipment.objects.all()
    return render(request, 'add_decommissioned_equipment.html', {
        'equipments': equipments,
    })

def add_decommissioned_equipment(request):
    if request.method == 'POST':
        equipment_id = request.POST.get('equipment')
        decommission_reason = request.POST.get('decommission_reason')
        decommission_date = request.POST.get('decommission_date')

        if not equipment_id or not decommission_reason or not decommission_date:
            messages.error(request, 'Please fill out all required fields.')
            return redirect('add_decommissioned_equipment_page')

        try:
            DecommissionedEquipment.objects.create(
                equipment_id=equipment_id,
                decommission_reason=decommission_reason,
                decommission_date=decommission_date
            )
            messages.success(request, 'Decommissioned Equipment added successfully!')
            return redirect('decommissioned_equipment_list')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('add_decommissioned_equipment_page')

    return redirect('add_decommissioned_equipment_page')


def edit_decommissioned_equipment(request, id):
    decommissioned_equipment = get_object_or_404(DecommissionedEquipment, id=id)

    if request.method == 'POST':
        form = DecommissionedEquipmentForm(request.POST, instance=decommissioned_equipment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Decommissioned Equipment updated successfully!')
            return redirect('decommissioned_equipment_list')
    else:
        form = DecommissionedEquipmentForm(instance=decommissioned_equipment)

    return render(request, 'edit_decommissioned_equipment.html', {'form': form, 'decommissioned_equipment': decommissioned_equipment})


#--------------------------------------------------------------------------------------
def maintenance_type_list(request):
    maintenance_types = MaintenanceType.objects.all()
    context = {
        'title': 'Maintenance Types',
        'item_list': maintenance_types,
        'edit_url': 'edit_maintenance_type',
    }
    return render(request, 'maintenance_type_list.html', context)

def add_maintenance_type_page(request):
    return render(request, 'add_maintenance_type.html')

def add_maintenance_type(request):
    if request.method == 'POST':
        maintenance_type = request.POST.get('maintenance_type')
        description = request.POST.get('description')

        if not maintenance_type:
            messages.error(request, 'Please fill out all required fields.')
            return redirect('add_maintenance_type_page')

        try:
            MaintenanceType.objects.create(
                maintenance_type=maintenance_type,
                description=description
            )
            messages.success(request, 'Maintenance Type added successfully!')
            return redirect('maintenance_type_list')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('add_maintenance_type_page')

    return redirect('add_maintenance_type_page')

def edit_maintenance_type(request, id):
    maintenance_type = get_object_or_404(MaintenanceType, id=id)

    if request.method == 'POST':
        form = MaintenanceTypeForm(request.POST, instance=maintenance_type)
        if form.is_valid():
            form.save()
            messages.success(request, 'Maintenance Type updated successfully!')
            return redirect('maintenance_type_list')
    else:
        form = MaintenanceTypeForm(instance=maintenance_type)

    return render(request, 'edit_maintenance_type.html', {'form': form, 'maintenance_type': maintenance_type})
#--------------------------------------------------------------------------------------------

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
        'spare_parts': SparePart.objects.all(),
    }

    if request.method == 'POST':
        # Get form data
        equipment_id = request.POST.get('equipment')
        assigned_technicians = request.POST.getlist('assigned_technicians')
        branch_id = request.POST.get('branch')
        maintenance_type_id = request.POST.get('maintenance_type')
        spare_parts = request.POST.getlist('spare_parts[]')  # List of spare part IDs
        spare_part_quantities = request.POST.getlist('spare_part_quantities[]')  # List of quantities
        remark = request.POST.get('remark')
        procedure = request.POST.get('procedure')
        problems = request.POST.get('problems')
        status = request.POST.get('status')

        # Validate required fields
        if not equipment_id or not assigned_technicians or not branch_id or not maintenance_type_id or not status:
            messages.error(request, 'Please fill out all required fields.')
            return render(request, 'add_maintenance.html', context)

        try:
            # Create and save the MaintenanceRecord object
            maintenance = MaintenanceRecord.objects.create(
                equipment_id=equipment_id,
                branch_id=branch_id,
                maintenance_type_id=maintenance_type_id,
                remark=remark,
                procedure=procedure,
                problems=problems,
                status=status,
            )
            maintenance.assigned_technicians.set(assigned_technicians)

            # Handle spare parts and quantities
            for spare_part_id, quantity_used in zip(spare_parts, spare_part_quantities):
                if not spare_part_id or not quantity_used:
                    continue  # Skip empty fields

                spare_part = SparePart.objects.get(id=spare_part_id)
                quantity_used = int(quantity_used)

                if spare_part.quantity < quantity_used:
                    messages.error(request, f'Not enough quantity for {spare_part.name}.')
                    maintenance.delete()  # Rollback the maintenance record
                    return render(request, 'add_maintenance.html', context)

                # Deduct the quantity from the spare part
                spare_part.quantity -= quantity_used
                spare_part.save()

                # Create SparePartUsage record
                SparePartUsage.objects.create(
                    maintenance_record=maintenance,
                    spare_part=spare_part,
                    quantity_used=quantity_used,
                )

            messages.success(request, 'Maintenance record added successfully!')
            return redirect('maintenance_list')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return render(request, 'add_maintenance.html', context)

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
    spare_parts = SparePart.objects.all()  # Fetch all spare parts
    spare_part_usages = SparePartUsage.objects.filter(maintenance_record=maintenance)  # Fetch existing spare part usages

    if request.method == 'POST':
        # Get form data
        equipment_id = request.POST.get('equipment')
        assigned_technicians = request.POST.getlist('assigned_technicians')
        branch_id = request.POST.get('branch')
        maintenance_type_id = request.POST.get('maintenance_type')
        spare_parts_post = request.POST.getlist('spare_parts[]')  # List of spare part IDs from the form
        spare_part_quantities = request.POST.getlist('spare_part_quantities[]')  # List of quantities from the form
        remark = request.POST.get('remark')
        procedure = request.POST.get('procedure')
        problems = request.POST.get('problems')
        status = request.POST.get('status')

        # Validate required fields
        if not equipment_id or not assigned_technicians or not branch_id or not maintenance_type_id or not status:
            messages.error(request, 'Please fill out all required fields.')
            return render(request, 'edit_maintenance.html', {
                'maintenance': maintenance,
                'spare_parts': spare_parts,
                'spare_part_usages': spare_part_usages,
            })

        try:
            # Update the MaintenanceRecord object
            maintenance.equipment_id = equipment_id
            maintenance.branch_id = branch_id
            maintenance.maintenance_type_id = maintenance_type_id
            maintenance.remark = remark
            maintenance.procedure = procedure
            maintenance.problems = problems
            maintenance.status = status
            maintenance.save()
            maintenance.assigned_technicians.set(assigned_technicians)

            # Step 1: Add back the old quantities to the spare parts
            for usage in spare_part_usages:
                spare_part = usage.spare_part
                spare_part.quantity += usage.quantity_used  # Add back the old quantity
                spare_part.save()

            # Step 2: Process the new spare parts and quantities
            for spare_part_id, quantity_used in zip(spare_parts_post, spare_part_quantities):
                if not spare_part_id or not quantity_used:
                    continue  # Skip empty fields

                spare_part_id = int(spare_part_id)
                quantity_used = int(quantity_used)

                # Get the spare part
                spare_part = SparePart.objects.get(id=spare_part_id)

                # Check if the new quantity exceeds the available stock
                if spare_part.quantity < quantity_used:
                    messages.error(request, f'Not enough quantity for {spare_part.name}. Available: {spare_part.quantity}')
                    # Rollback the old quantities
                    for usage in spare_part_usages:
                        spare_part = usage.spare_part
                        spare_part.quantity -= usage.quantity_used  # Deduct the old quantity (undo Step 1)
                        spare_part.save()
                    return render(request, 'edit_maintenance.html', {
                        'maintenance': maintenance,
                        'spare_parts': spare_parts,
                        'spare_part_usages': spare_part_usages,
                    })

                # Deduct the new quantity from the spare part
                spare_part.quantity -= quantity_used
                spare_part.save()

                # Create or update the SparePartUsage record
                SparePartUsage.objects.update_or_create(
                    maintenance_record=maintenance,
                    spare_part=spare_part,
                    defaults={'quantity_used': quantity_used},
                )

            # Step 3: Delete any remaining spare part usages that were not in the form
            SparePartUsage.objects.filter(maintenance_record=maintenance).exclude(
                spare_part_id__in=[int(id) for id in spare_parts_post]
            ).delete()

            messages.success(request, 'Maintenance record updated successfully!')
            return redirect('maintenance_list')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return render(request, 'edit_maintenance.html', {
                'maintenance': maintenance,
                'spare_parts': spare_parts,
                'spare_part_usages': spare_part_usages,
            })

    # For GET requests, pre-fill the form and spare parts
    form = MaintenanceRecordForm(instance=maintenance)
    return render(request, 'edit_maintenance.html', {
        'form': form,
        'maintenance': maintenance,
        'spare_parts': spare_parts,
        'spare_part_usages': spare_part_usages,
    })

def branch_list(request):
    branches = Branch.objects.all()
    context = {
        'title': 'Branches',
        'item_list': branches,
        'edit_url': 'edit_branch',
    }
    return render(request, 'branch_list.html', context)

def add_branch_page(request):
    return render(request, 'add_branch.html')




def add_branch(request):
    if request.method == 'POST':
        form = BranchForm(request.POST)  # Bind the form to the POST data
        if form.is_valid():  # Validate the form
            form.save()  # Save the form data to the database
            messages.success(request, 'Branch added successfully!')
            return redirect('branch_list')  # Redirect to the branch list page
    else:
        form = BranchForm()  # Create an empty form for GET requests

    # Render the form in the template
    return render(request, 'add_branch.html', {'form': form})

def edit_branch(request, id):
    branch = get_object_or_404(Branch, id=id)
    if request.method == 'POST':
        form = BranchForm(request.POST, instance=branch)
        if form.is_valid():
            form.save()
            messages.success(request, 'Branch updated successfully!')
            return redirect('branch_list')
    else:
        form = BranchForm(instance=branch)
    return render(request, 'edit_branch.html', {'form': form, 'branch': branch})
#---------------------------------------------------------------------------------------------

def user_profile_list(request):
    user_profiles = UserProfile.objects.all()
    context = {
        'title': 'User Profiles',
        'item_list': user_profiles,
        'edit_url': 'edit_user_profile',
    }
    return render(request, 'user_profile_list.html', context)

def add_user_profile_page(request):
    # Fetch all branches from the database
    branches = Branch.objects.all()

    # Debugging: Print the choices to the console
    print("Roles:", UserProfile.ROLE_CHOICES)
    print("Branches:", branches)

    # Pass the DEPARTMENT_CHOICES, ROLE_CHOICES, and branches to the template
    context = {
        'roles': UserProfile.ROLE_CHOICES,
        'branches': branches,  # Pass the branches queryset
    }
    return render(request, 'add_user_profile.html', context)


def add_user_profile(request):
    if request.method == 'POST':
        first_name = request.POST.get('firstName')
        last_name = request.POST.get('lastName')
        username = request.POST.get('username')
        email = request.POST.get('email')  # Email is optional
        password = request.POST.get('password')
        role = request.POST.get('role')  # Role as a string
        branch_id = request.POST.get('branch')
        is_active = request.POST.get('is_active')  # Default to active
        is_active = is_active.capitalize()

        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('add_user_profile_page')

        # Create the User
        user = User.objects.create_user(
            username=username,
            email=email,  # Email is optional
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_active=is_active  # Set user active status
        )

        # Create UserProfile
        user_profile = UserProfile(
            user=user,
            branch_id=branch_id,
            role=role  # Pass the role string
        )
        user_profile.save()

        messages.success(request, 'User created successfully')
        return redirect('user_profile_list')  # Redirect to the user list page

    return render(request, 'add_user_profile.html')
def edit_user_profile(request, id):
    user_profile = get_object_or_404(UserProfile, id=id)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            # Update the user's active status
            is_active = request.POST.get('is_active', 'on') == 'on'
            user_profile.user.is_active = is_active
            user_profile.user.save()  # Save the User model

            # Handle password update
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirmPassword')
            if password and confirm_password:
                if password == confirm_password:
                    # Update the user's password
                    user_profile.user.password = make_password(password)
                    user_profile.user.save()
                    messages.success(request, 'Password updated successfully!')
                else:
                    messages.error(request, 'Passwords do not match!')
                    return redirect('edit_user_profile', id=id)

            form.save()  # Save the UserProfile model
            messages.success(request, 'User Profile updated successfully!')
            return redirect('user_profile_list')
    else:
        form = UserProfileForm(instance=user_profile)
    
    return render(request, 'edit_user_profile.html', {
        'form': form,
        'user_profile': user_profile,
    })
def check_username(request):
    username = request.GET.get('username')
    exists = User.objects.filter(username=username).exists()
    return JsonResponse({'exists': exists})

@login_required()
def dashboard(request):
    return render(request, 'dashboard.html')

@login_required()
def equipment(request):
    return render(request, 'equipment.html')