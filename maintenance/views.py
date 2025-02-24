from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.http import Http404
from datetime import datetime
from django.db.models import Count, Q
from datetime import datetime, timedelta
from .Forms import EquipmentForm, SparePartForm, MaintenanceRecordForm, ChemicalForm, ManufacturerForm, WorkOrderForm, SparePartUsageForm, DecommissionedEquipmentForm, MaintenanceTypeForm, BranchForm, UserProfileForm, RestockSparePartForm

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

def get_notifications(user):
    return Notification.objects.filter(user=user, is_read=False).order_by('-timestamp')[:10]



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




@login_required
def my_profile(request):
    # Get the current user's profile
    user_profile = UserProfile.objects.get(user=request.user)
    notifications = get_notifications(request.user)

    
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
                return redirect('my_profile', {'notifications':notifications})
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('my_profile', { 'active_page': 'profile','notifications':notifications,
})
    
    return render(request, 'my_profile.html', {
        'user_profile': user_profile,
                'active_page': 'profile',
                'notifications':notifications

        
    })


def manufacturer_list(request):
    user_branch = request.user.userprofile.branch
    manufacturers = Manufacturer.objects.filter(site = user_branch)
    notifications = get_notifications(request.user)

    context = {
        'active_page': 'manufacturer_list',
        'title': 'Manufacturers',
        'item_list': manufacturers,
        'edit_url': 'edit_manufacturer',
        'notifications':notifications
    }
    return render(request, 'manufacturer_list.html', context)

def add_manufacturer_page(request):
    notifications = get_notifications(request.user)

    
    context = {
    'active_page': 'manufacturer_list', 'notifications':notifications}
    
    return render(request, 'add_manufacturer.html', context)

def add_manufacturer(request):
    notifications = get_notifications(request.user)

    # Get the user's branch
    if request.user.is_authenticated:
        branch = request.user.userprofile.branch  # Ensure this matches your UserProfile model
    else:
        branch = None  # Handle unauthenticated users

    if request.method == 'POST':
        # Get form data
        name = request.POST.get('name')
        description = request.POST.get('description')
        site = request.POST.get('site')  # This will be the branch ID
        contact_email = request.POST.get('contact_email')
        contact_phone_number = request.POST.get('contact_phone_number')
        address = request.POST.get('address')

        # Validate required fields
        if not name or not site:
            messages.error(request, 'Please fill out all required fields.')
            return render(request, 'add_manufacturer.html', {'active_page': 'manufacturer_list', 'branch': branch, 'notifications':notifications})

        try:
            # Create the manufacturer
            Manufacturer.objects.create(
                name=name,
                description=description,
                site_id=site,  # Use site_id to assign the branch
                contact_email=contact_email,
                contact_phone_number=contact_phone_number,
                address=address
            )
            messages.success(request, 'Manufacturer added successfully!')
            return redirect('manufacturer_list')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return render(request, 'add_manufacturer.html', {'active_page': 'manufacturer_list', 'branch': branch, 'notifications':notifications})

    return render(request, 'add_manufacturer.html', {'active_page': 'manufacturer_list', 'branch': branch, 'notifications':notifications})

def edit_manufacturer(request, id):
    manufacturer = get_object_or_404(Manufacturer, id=id)
    branch = request.user.userprofile.branch
    notifications = get_notifications(request.user)


   

    if request.method == 'POST':
        form = ManufacturerForm(request.POST, instance=manufacturer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Manufacturer updated successfully!')
            return redirect('manufacturer_list')
    else:
        form = ManufacturerForm(instance=manufacturer)

    return render(request, 'edit_manufacturer.html', {'form': form, 'manufacturer': manufacturer,  'active_page': 'manufacturer_list', 'branch':branch, 'notifications':notifications})

#----------------------------------------------------------------------------------

def work_order_list(request):
    user_branch = request.user.userprofile.branch

    work_orders = WorkOrder.objects.filter(branch = user_branch)
    notifications = get_notifications(request.user)

    context = {
        'active_page': 'work_order_list',
        'title': 'Work Orders',
        'item_list': work_orders,
        'edit_url': 'edit_work_order',
        'notifications':notifications,
    }
    return render(request, 'work_order_list.html', context)

def add_work_order_page(request):
    notifications = get_notifications(request.user)
    user_branch = request.user.userprofile.branch

    equipments = Equipment.objects.filter(branch=user_branch)
    
    return render(request, 'add_work_order.html', {
        'equipments': equipments,
        'branch': user_branch,
        'notifications': notifications,
        'active_page': 'work_order_list',

    })

def add_work_order(request):
    notifications = get_notifications(request.user)

    if request.method == 'POST':
        branch = request.POST.get('branch')
        equipment_id = request.POST.get('equipment')
        description = request.POST.get('description')
        status = 'Pending'  # Default status

        if not branch or not equipment_id or not description:
            messages.error(request, 'Please fill out all required fields.')
            return redirect('add_work_order_page')

        try:
            work_order = WorkOrder.objects.create(
                requester=request.user,
                branch_id=branch,
                equipment_id=equipment_id,
                description=description,
                status=status
            )
            messages.success(request, 'Work Order added successfully!')

            # Send notification to the MD Manager of the same branch
            manager = User.objects.filter(userprofile__branch=branch, userprofile__role='MD manager').first()
            if manager:
                Notification.objects.create(
                    user=manager,
                    type = "maintenance",
                    message=f'New work order: {work_order.equipment.name}.',
                )

            return redirect('work_order_list')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('add_work_order_page')

    return redirect('add_work_order_page')

def edit_work_order(request, id):
    user_branch = request.user.userprofile.branch
    notifications = get_notifications(request.user)
    spare_parts = SparePart.objects.filter(branch=user_branch)
    work_order = get_object_or_404(WorkOrder, id=id)
    assigned_technician_ids = work_order.assigned_technicians.values_list('id', flat=True)

    if request.method == 'POST':
        # Get form data
        assigned_technicians = request.POST.getlist('assigned_technicians[]')
        spare_parts_post = request.POST.getlist('spare_parts[]')
        spare_part_quantities = request.POST.getlist('spare_part_quantities[]')

        try:
            # Update assigned technicians
            work_order.assigned_technicians.set(assigned_technicians)

            # Step 1: Add back the old quantities to the spare parts
            spare_part_usages = SparePartUsage.objects.filter(work_order=work_order)
            for usage in spare_part_usages:
                spare_part = usage.spare_part
                spare_part.quantity += usage.quantity_used
                spare_part.save()

            # Step 2: Process the new spare parts and quantities
            for spare_part_id, quantity_used in zip(spare_parts_post, spare_part_quantities):
                # Skip if spare_part_id or quantity_used is empty
                if not spare_part_id.strip() or not quantity_used.strip():
                    continue  # Skip empty fields

                # Skip if spare_part_id is not a valid integer
                try:
                    spare_part_id = int(spare_part_id)
                except ValueError:
                    continue  # Skip invalid spare_part_id (e.g., non-numeric values)

                # Skip if quantity_used is not a valid integer
                try:
                    quantity_used = int(quantity_used)
                except ValueError:
                    continue  # Skip invalid quantities (e.g., non-numeric values)

                # Get the spare part
                spare_part = SparePart.objects.get(id=spare_part_id)

                # Check if the new quantity exceeds the available stock
                if spare_part.quantity < quantity_used:
                    messages.error(request, f'Not enough quantity for {spare_part.name}. Available: {spare_part.quantity}')
                    # Rollback the old quantities
                    for usage in spare_part_usages:
                        spare_part = usage.spare_part
                        spare_part.quantity -= usage.quantity_used
                        spare_part.save()
                    return redirect('edit_work_order', id=work_order.id)

                # Deduct the new quantity from the spare part
                spare_part.quantity -= quantity_used
                spare_part.save()
                check_low_spare_parts(spare_part)

                # Create or update the SparePartUsage record
                SparePartUsage.objects.update_or_create(
                    work_order=work_order,  # Use work_order instead of maintenance_record
                    spare_part=spare_part,
                    defaults={'quantity_used': quantity_used},
                )

            # Step 3: Delete any remaining spare part usages that were not in the form
            SparePartUsage.objects.filter(work_order=work_order).exclude(
                spare_part_id__in=[int(id) for id in spare_parts_post if id.strip()]
            ).delete()

            # Notify assigned technicians
            for technician_id in assigned_technicians:
                technician = User.objects.get(id=technician_id)
                Notification.objects.create(
                    user=technician,
                    type = "work_order",
                    message=f'You have been assigned a new work order task: {work_order}.',
                )

            messages.success(request, 'Work order updated successfully!')
            return redirect('work_order_list')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('edit_work_order', id=work_order.id)

    # For GET requests, pre-fill the form and spare parts
    context = {
        'work_order': work_order,
        'technicians': User.objects.filter(userprofile__branch=user_branch, userprofile__role='TEC'),
        'assigned_technician_ids': assigned_technician_ids,
        'active_page': 'work_order_list',
        'notifications': notifications,
        'spare_parts': spare_parts,
    }
    return render(request, 'edit_work_order.html', context)
#------------------------------------------------------------------------------------

#  user_branch = request.user.userprofile.branch
#     notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-timestamp')[:10]

#     context = {
#         'equipments': Equipment.objects.filter(branch=user_branch),
#         'technicians': User.objects.filter(userprofile__branch=user_branch, userprofile__role='TEC'),
#         'branch': user_branch,
#         'maintenance_types': MaintenanceType.objects.filter(branch=user_branch),
#         'work_orders': WorkOrder.objects.filter(branch=user_branch),
#         'spare_parts': SparePart.objects.filter(branch=user_branch),
#         'active_page': 'maintenance_list',
#         'notifications': notifications,
#     }







#---------------------------------------------------------------------------------------

def spare_part_usage_list(request):
    notifications = get_notifications(request.user)
    user_branch = request.user.userprofile.branch

    spare_part_usages = SparePartUsage.objects.filter(maintenance_record__branch=user_branch)
    context = {
        'active_page': 'spare_part_usage_list',
        'title': 'Spare Part Usages',
        'item_list': spare_part_usages,
        'edit_url': 'edit_spare_part_usage',
        'notifications':notifications
        
    }
    return render(request, 'spare_part_usage_list.html', context)

def add_spare_part_usage_page(request):
    notifications = get_notifications(request.user)
    user_branch = request.user.userprofile.branch

    maintenance_records = MaintenanceRecord.objects.filter(branch = user_branch)
    spare_parts = SparePart.objects.all()
    return render(request, 'add_spare_part_usage.html', {
        'maintenance_records': maintenance_records,
        'spare_parts': spare_parts,
    'active_page': 'spare_part_usage_list',
    'notifications': notifications
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
    notifications = get_notifications(request.user)


    if request.method == 'POST':
        form = SparePartUsageForm(request.POST, instance=spare_part_usage)
        if form.is_valid():
            form.save()
            messages.success(request, 'Spare Part Usage updated successfully!')
            return redirect('spare_part_usage_list')
    else:
        form = SparePartUsageForm(instance=spare_part_usage)

    return render(request, 'edit_spare_part_usage.html', {'form': form, 'spare_part_usage': spare_part_usage, 'active_page': 'spare_part_usage_list', 'notifications':notifications})

#------------------------------------------------------------------------------------
def decommissioned_equipment_list(request):
    decommissioned_equipments = DecommissionedEquipment.objects.all()
    notifications = get_notifications(request.user)

    context = {
        'active_page': 'decommissioned_equipment_list',
        'title': 'Decommissioned Equipments',
        'item_list': decommissioned_equipments,
        'edit_url': 'edit_decommissioned_equipment',
        'notifications':notifications
    }
    return render(request, 'decommissioned_equipment_list.html', context)

def add_decommissioned_equipment_page(request):
    notifications = get_notifications(request.user)
    equipments = Equipment.objects.filter(branch = request.user.userprofile.branch)
    return render(request, 'add_decommissioned_equipment.html', {
        'equipments': equipments,'active_page': 'decommissioned_equipment_list','notifications':notifications
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
    notifications = get_notifications(request.user)


    if request.method == 'POST':
        form = DecommissionedEquipmentForm(request.POST, instance=decommissioned_equipment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Decommissioned Equipment updated successfully!')
            return redirect('decommissioned_equipment_list')
    else:
        form = DecommissionedEquipmentForm(instance=decommissioned_equipment)

    return render(request, 'edit_decommissioned_equipment.html', {'form': form, 'decommissioned_equipment': decommissioned_equipment, 'active_page': 'decommissioned_equipment_list','notifications':notifications})


#--------------------------------------------------------------------------------------
def maintenance_type_list(request):
    user_branch = request.user.userprofile.branch
    notifications = get_notifications(request.user)


    maintenance_types = MaintenanceType.objects.filter(branch =user_branch )
    context = {
        'active_page': 'maintenance_type_list',
        'title': 'Maintenance Types',
        'item_list': maintenance_types,
        'edit_url': 'edit_maintenance_type',
        'notifications':notifications
    }
    return render(request, 'maintenance_type_list.html', context)

def add_maintenance_type_page(request):
    user_branch = request.user.userprofile.branch
    notifications = get_notifications(request.user)


    return render(request, 'add_maintenance_type.html',{ 'active_page': 'maintenance_type_list', 'branch': user_branch, 'notifications':notifications
})

def add_maintenance_type(request):
    user_branch = request.user.userprofile.branch
    notifications = get_notifications(request.user)
   

    if request.method == 'POST':
        maintenance_type = request.POST.get('maintenance_type')
        branch_id = request.POST.get('branch')  # Get the branch ID from the form
        description = request.POST.get('description')

        if not maintenance_type:
            messages.error(request, 'Please fill out all required fields.')
            return render(request, 'add_maintenance_type.html', {
                'active_page': 'maintenance_type_list',
                'branch': user_branch,
                'notifications':notifications
                
            })

        try:
            # Fetch the Branch instance using the branch_id
            branch = Branch.objects.get(id=branch_id)

            # Create the MaintenanceType object
            MaintenanceType.objects.create(
                maintenance_type=maintenance_type,
                branch=branch,  # Pass the Branch instance
                description=description
            )
            messages.success(request, 'Maintenance Type added successfully!')
            return redirect('maintenance_type_list')
        except Branch.DoesNotExist:
            messages.error(request, 'Invalid branch selected.')
            return render(request, 'add_maintenance_type.html', {
                'active_page': 'maintenance_type_list',
                'branch': user_branch
            })
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return render(request, 'add_maintenance_type.html', {
                'active_page': 'maintenance_type_list',
                'branch': user_branch
            })

    # For GET requests, render the add maintenance type page with context
    return render(request, 'add_maintenance_type.html', {
        'active_page': 'maintenance_type_list',
        'branch': user_branch
    })
def edit_maintenance_type(request, id):
    user_branch = request.user.userprofile.branch
    notifications = get_notifications(request.user)


    maintenance_type = get_object_or_404(MaintenanceType, id=id)

    if request.method == 'POST':
        form = MaintenanceTypeForm(request.POST, instance=maintenance_type)
        if form.is_valid():
            form.save()
            messages.success(request, 'Maintenance Type updated successfully!')
            return redirect('maintenance_type_list')
    else:
        form = MaintenanceTypeForm(instance=maintenance_type)

    return render(request, 'edit_maintenance_type.html', {'form': form, 'maintenance_type': maintenance_type,  'active_page': 'maintenance_type_list','notifications':notifications})
#--------------------------------------------------------------------------------------------

def equipment_list(request):
    user_branch = request.user.userprofile.branch
    notifications = get_notifications(request.user)


    equipments = Equipment.objects.filter(branch = user_branch)  # Fetch all equipment
    context = {
        'active_page': 'equipment_list',
        'title': 'Equipments',
        'item_list': equipments,
        'edit_url': 'edit_equipment',  # Assuming you have an edit view set up
        'notifications':notifications
    }
    return render(request, 'equipment_list.html', context)



def add_equipment_page(request):
    notifications = get_notifications(request.user)

    user_branch = request.user.userprofile.branch
    manufacturers = Manufacturer.objects.filter(site = user_branch)
    branch = user_branch
    return render (request, 'equipment.html', {
                'manufacturers': manufacturers,
                'branch': branch,
                'active_page': 'equipment_list',
                'notifications':notifications
            })


def add_equipment(request):
    notifications = get_notifications(request.user)

    equipment= Equipment.objects.all()
    # Get the user's branch
    user_branch = request.user.userprofile.branch

    # Filter manufacturers by the user's branch
    manufacturers = Manufacturer.objects.filter(site=user_branch)

    if request.method == 'POST':
        # Get form data
        name = request.POST.get('name')
        equipment_type = request.POST.get('equipment_type')
        manufacturer_id = request.POST.get('manufacturer')
        model_number = request.POST.get('model_number')
        serial_number = request.POST.get('serial_number')
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
        if not name or not equipment_type or not manufacturer_id or not model_number or not serial_number or not location or not installation_date or not status:
            messages.error(request, 'Please fill out all required fields.')
            context = {
                'manufacturers': manufacturers,
                'branch': user_branch,  # Pass the user's branch to the template
                'active_page': 'equipment_list',
                'notifications':notifications
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
                branch=user_branch,  # Set the branch to the user's branch
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
                'branch': user_branch,  # Pass the user's branch to the template
                'active_page': 'equipment_list',
                'notifications':notifications,
            }
            return render(request, 'equipment.html', context)
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            context = {
                'manufacturers': manufacturers,
                'branch': user_branch,  # Pass the user's branch to the template
                'active_page': 'equipment_list',
                'notifications':notifications
            }
            return render(request, 'equipment.html', context)

    # For GET requests, render the form with manufacturers and the user's branch
    context = {
        'manufacturers': manufacturers,
        'branch': user_branch,  # Pass the user's branch to the template
        'active_page': 'equipment_list',
        'notifications':notifications
    }
    return render(request, 'equipment.html', context)
def edit_equipment(request, id):
    notifications = get_notifications(request.user)

    equipment = get_object_or_404(Equipment, id=id)  # Fetch the equipment instance

    if request.method == 'POST':
        form = EquipmentForm(request.POST, instance=equipment)
        if form.is_valid():
            form.save()  # Save the changes to the database
            messages.success(request, 'Equipment changed successfully')


            return redirect('equipment_list')  # Redirect to the equipment list after saving
    else:
        form = EquipmentForm(instance=equipment)  # Pre-fill the form with the current data

    return render(request, 'edit_equipment.html', {'form': form, 'equipment': equipment, 'active_page': 'equipment_list','notifications':notifications})

#-----------------------------------------------------------------------------------------------

def spare_part_list(request):
    notifications = get_notifications(request.user)

    user_branch = request.user.userprofile.branch

    spare_parts = SparePart.objects.filter(branch = user_branch)  # Fetch all sparepart
    context = {
        'active_page': 'spare_part_list',
        'title': 'Spare Parts',
        'item_list': spare_parts,
        'edit_url': 'edit_spare_part',  # Assuming you have an edit view set up
        'notifications':notifications
    }
    return render(request, 'spare_part_list.html', context)

def add_spare_part_page(request):
    notifications = get_notifications(request.user)

    user_branch = request.user.userprofile.branch

    branch = user_branch
    return render (request, 'add_spare_part.html', {
                'branch': branch,
                'active_page': 'spare_part_list',
                'notifications':notifications

            })

def add_spare_part(request):
    notifications = get_notifications(request.user)

    user_branch = request.user.userprofile.branch

    # Define context with default values
    context = {
        'branch': user_branch,
        'active_page': 'spare_part_list',
        'notifications':notifications
    }

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
            return render(request, 'add_spare_part.html', context)

        try:
            # Convert quantity and price to appropriate types
            quantity = int(quantity)
            price = float(price)

            # Check if the part number already exists for the selected branch
            

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
            return redirect('spare_part_list')  # Redirect to the spare part list page
        except ValueError as e:
            messages.error(request, f'Invalid input: {str(e)}')
            return render(request, 'add_spare_part.html', context)
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return render(request, 'add_spare_part.html', context)

    # For GET requests, render the form with branches
    return render(request, 'add_spare_part.html', context)
def edit_spare_part(request, id):
    notifications = get_notifications(request.user)

    spare_part = get_object_or_404(SparePart, id=id)  # Fetch the spare part instance

    if request.method == 'POST':
        form = SparePartForm(request.POST, instance=spare_part)
        if form.is_valid():
            form.save()  # Save the changes to the database
            messages.success(request, 'Spare part updated successfully!')
            return redirect('spare_part_list')  # Redirect to the spare part list after saving
    else:
        form = SparePartForm(instance=spare_part)  # Pre-fill the form with the current data

    return render(request, 'edit_spare_part.html', {'form': form, 'spare_part': spare_part,'active_page': 'spare_part_list','notifications':notifications
})


 
    
    
def add_chemical_page(request):
    notifications = get_notifications(request.user)

    branches = Branch.objects.all()  # Fetch all branches for the dropdown
    return render(request, 'add_chemical.html', {
        'branches': branches,
        'active_page': 'chemical_list',
        'notifications':notifications

    })

def add_chemical(request):
    notifications = get_notifications(request.user)

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
                'active_page': 'chemical_list',
                'notifications':notifications

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
                'active_page': 'chemical_list',
                'notifications':notifications

            }
            return render(request, 'add_chemical.html', context)
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            context = {
                'branches': branches,
                'active_page': 'chemical_list',
                'notifications':notifications
            }
            return render(request, 'add_chemical.html', context)

    # For GET requests, render the form with branches
    context = {
        'branches': branches,
        'active_page': 'chemical_list',
        'notifications':notifications

    }
    return render(request, 'add_chemical.html', context)

def chemical_list(request):
    notifications = get_notifications(request.user)

    chemicals = Chemical.objects.all()  # Fetch all chemicals
    context = {
        'active_page': 'chemical_list',
        'title': 'Chemical List',
        'item_list': chemicals,
        'edit_url': 'edit_chemical',  # URL name for editing chemicals
        'notifications':notifications
    }
    return render(request, 'chemical_list.html', context)


def edit_chemical(request, id):
    notifications = get_notifications(request.user)

    chemical = get_object_or_404(Chemical, id=id)  # Fetch the chemical instance

    if request.method == 'POST':
        form = ChemicalForm(request.POST, instance=chemical)
        if form.is_valid():
            form.save()  # Save the changes to the database
            messages.success(request, 'Chemical updated successfully!')
            return redirect('chemical_list')  # Redirect to the chemical list
    else:
        form = ChemicalForm(instance=chemical)  # Pre-fill the form with the current data

    return render(request, 'edit_chemical.html', {'form': form, 'chemical': chemical, 'active_page': 'chemical_list','notifications':notifications
})
    
    

def add_maintenance_page(request):
    notifications = get_notifications(request.user)

    user_branch = request.user.userprofile.branch

    context = {
        'equipments': Equipment.objects.filter(branch=user_branch),
        'technicians': User.objects.filter(
            userprofile__branch=user_branch,  # Filter by branch
            userprofile__role='TEC'  # Filter by role (Technician)
        ),
        'branch': user_branch,
        'maintenance_types': MaintenanceType.objects.filter(branch=user_branch),
        'work_orders': WorkOrder.objects.filter(branch=user_branch),
        'spare_parts': SparePart.objects.filter(branch=user_branch),
        'active_page': 'maintenance_list',
        'notifications':notifications
    }
    return render(request, 'add_maintenance.html', context)

def add_maintenance(request):
    user_branch = request.user.userprofile.branch
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-timestamp')[:10]

    context = {
        'equipments': Equipment.objects.filter(branch=user_branch),
        'technicians': User.objects.filter(userprofile__branch=user_branch, userprofile__role='TEC'),
        'branch': user_branch,
        'maintenance_types': MaintenanceType.objects.filter(branch=user_branch),
        'work_orders': WorkOrder.objects.filter(branch=user_branch),
        'spare_parts': SparePart.objects.filter(branch=user_branch),
        'active_page': 'maintenance_list',
        'notifications': notifications,
    }

    if request.method == 'POST':
        equipment_id = request.POST.get('equipment')
        assigned_technicians = request.POST.getlist('assigned_technicians[]')
        branch_id = request.POST.get('branch')
        maintenance_type_id = request.POST.get('maintenance_type')
        spare_parts = request.POST.getlist('spare_parts[]')
        spare_part_quantities = request.POST.getlist('spare_part_quantities[]')
        remark = request.POST.get('remark')
        procedure = request.POST.get('procedure')
        problems = request.POST.get('problems')
        status = request.POST.get('status')

        # if not equipment_id or not assigned_technicians or not branch_id or not maintenance_type_id or not status:
        #     messages.error(request, 'Please fill out all required fields.')
        #     return render(request, 'add_maintenance.html', context)

        try:
            maintenance = MaintenanceRecord.objects.create(
                equipment_id=equipment_id,
                branch_id=branch_id,
                maintenance_type_id=maintenance_type_id,
                remark=remark,
                procedure=procedure,
                problems=problems,
                status='Not Started',
            )
            maintenance.assigned_technicians.set(assigned_technicians)

            for spare_part_id, quantity_used in zip(spare_parts, spare_part_quantities):
                if not spare_part_id or not quantity_used:
                    continue

                spare_part = SparePart.objects.get(id=spare_part_id)
                quantity_used = int(quantity_used)

                if spare_part.quantity < quantity_used:
                    messages.error(request, f'Not enough quantity for {spare_part.name}.')
                    maintenance.delete()
                    return render(request, 'add_maintenance.html', context)

                spare_part.quantity -= quantity_used
                spare_part.save()
                check_low_spare_parts(spare_part)

                SparePartUsage.objects.create(
                    maintenance_record=maintenance,
                    spare_part=spare_part,
                    quantity_used=quantity_used,
                )

            # Notify assigned technicians via system notifications
            for technician_id in assigned_technicians:
                technician = User.objects.get(id=technician_id)
                Notification.objects.create(
                    user=technician,
                    type = "maintenance",
                    message=f'You have been assigned a new maintenance task: {maintenance.equipment.name}.',
                )

            messages.success(request, 'Maintenance record added successfully!')
            print(notifications)

            return redirect('maintenance_list')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return render(request, 'add_maintenance.html', context)
    print(notifications)

    return render(request, 'add_maintenance.html', context)
def maintenance_list(request):
    notifications = get_notifications(request.user)

    user_branch = request.user.userprofile.branch

    maintenance_records = MaintenanceRecord.objects.filter(branch = user_branch )  # Fetch all maintenance records
    context = {
        'active_page': 'maintenance_list',
        'title': 'Maintenance List',
        'item_list': maintenance_records,
        'edit_url': 'edit_maintenance',  # URL name for editing maintenance records
        'notifications':notifications
    }
    return render(request, 'maintenance_list.html', context)
    

def edit_maintenance(request, id):
    notifications = get_notifications(request.user)
    user_branch = request.user.userprofile.branch
    maintenance = get_object_or_404(MaintenanceRecord, id=id)
    spare_parts = SparePart.objects.filter(branch=user_branch)
    spare_part_usages = SparePartUsage.objects.filter(maintenance_record=maintenance)

    if request.method == 'POST':
        # Get form data
        equipment_id = request.POST.get('equipment')
        assigned_technicians = request.POST.getlist('assigned_technicians')
        branch_id = request.POST.get('branch')
        maintenance_type_id = request.POST.get('maintenance_type')
        spare_parts_post = request.POST.getlist('spare_parts[]')
        spare_part_quantities = request.POST.getlist('spare_part_quantities[]')
        remark = request.POST.get('remark')
        procedure = request.POST.get('procedure')
        problems = request.POST.get('problems')
        status = request.POST.get('status')

        # Validate required fields
        # if not equipment_id  or not branch_id or not maintenance_type_id or not status:
        #     messages.error(request, 'Please fill out all required fields.')
        #     return render(request, 'edit_maintenance.html', {
        #         'maintenance': maintenance,
        #         'spare_parts': spare_parts,
        #         'spare_part_usages': spare_part_usages,
        #         'active_page': 'maintenance_list',
        #         'notifications': notifications,
                
        #     })

        try:
            # Update the MaintenanceRecord object
            # maintenance.equipment_id = equipment_id
            # maintenance.branch_id = branch_id
            maintenance.maintenance_type_id = maintenance_type_id
            maintenance.remark = remark
            maintenance.procedure = procedure
            maintenance.problems = problems
            # maintenance.status = status
            maintenance.save()
            # maintenance.assigned_technicians.set(assigned_technicians)

            # Step 1: Add back the old quantities to the spare parts
            for usage in spare_part_usages:
                spare_part = usage.spare_part
                spare_part.quantity += usage.quantity_used
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
                        spare_part.quantity -= usage.quantity_used
                        spare_part.save()
                        
                    return redirect(f'{request.path}?equipment={equipment_id}&maintenance_type={maintenance_type_id}&error=1')

                # Deduct the new quantity from the spare part
                spare_part.quantity -= quantity_used
                spare_part.save()
                check_low_spare_parts(spare_part)

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
                'active_page': 'maintenance_list',
                'notifications': notifications
            })

    # For GET requests, pre-fill the form and spare parts
    form = MaintenanceRecordForm(instance=maintenance)
    return render(request, 'edit_maintenance.html', {
        'form': form,
        'maintenance': maintenance,
        'spare_parts': spare_parts,
        'spare_part_usages': spare_part_usages,
        'active_page': 'maintenance_list',
        'notifications': notifications
    })
def branch_list(request):
    notifications = get_notifications(request.user)

    branches = Branch.objects.all()
    context = {
        'active_page': 'branch_list',
        'title': 'Branches',
        'item_list': branches,
        'edit_url': 'edit_branch',
        'notifications':notifications
    }
    return render(request, 'branch_list.html', context)

def add_branch_page(request):
    notifications = get_notifications(request.user)

    return render(request, 'add_branch.html',{ 'active_page': 'branch_list','notifications':notifications})




def add_branch(request):
    notifications = get_notifications(request.user)

    if request.method == 'POST':
        form = BranchForm(request.POST)  # Bind the form to the POST data
        if form.is_valid():  # Validate the form
            form.save()  # Save the form data to the database
            messages.success(request, 'Branch added successfully!')
            return redirect('branch_list')  # Redirect to the branch list page
    else:
        form = BranchForm()  # Create an empty form for GET requests

    # Render the form in the template
    return render(request, 'add_branch.html', {'form': form,  'active_page': 'branch_list','notifications':notifications})

def edit_branch(request, id):
    notifications = get_notifications(request.user)

    branch = get_object_or_404(Branch, id=id)
    if request.method == 'POST':
        form = BranchForm(request.POST, instance=branch)
        if form.is_valid():
            form.save()
            messages.success(request, 'Branch updated successfully!')
            return redirect('branch_list',{ 'active_page': 'branch_list','notifications':notifications})
    else:
        form = BranchForm(instance=branch)
    return render(request, 'edit_branch.html', {'form': form, 'branch': branch, 'active_page': 'branch_list','notifications':notifications})
#---------------------------------------------------------------------------------------------

def user_profile_list(request):
    notifications = get_notifications(request.user)

    user_profiles = UserProfile.objects.all()
    context = {
        'active_page': 'user_profile_list',
        'title': 'User Profiles',
        'item_list': user_profiles,
        'edit_url': 'edit_user_profile',
        'notifications':notifications
    }
    return render(request, 'user_profile_list.html', context)

def add_user_profile_page(request):
    notifications = get_notifications(request.user)

    # Fetch all branches from the database
    branches = Branch.objects.all()

    # Debugging: Print the choices to the console
    print("Roles:", UserProfile.ROLE_CHOICES)
    print("Branches:", branches)

    # Pass the DEPARTMENT_CHOICES, ROLE_CHOICES, and branches to the template
    context = {
        'roles': UserProfile.ROLE_CHOICES,
        'branches': branches,  # Pass the branches queryset
         'active_page': 'user_profile_list',
         'notifications':notifications
    }
    return render(request, 'add_user_profile.html', context)


def add_user_profile(request):
    notifications = get_notifications(request.user)

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
            return redirect('add_user_profile_page', { 'active_page': 'user_profile_list','notifications':notifications})

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

    return render(request, 'add_user_profile.html', { 'active_page': 'user_profile_list',})
def edit_user_profile(request, id):
    notifications = get_notifications(request.user)

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
                    return redirect('edit_user_profile', id=id, )

            form.save()  # Save the UserProfile model
            messages.success(request, 'User Profile updated successfully!')
            return redirect('user_profile_list', { 'active_page': 'user_profile_list',})
    else:
        form = UserProfileForm(instance=user_profile)
    
    return render(request, 'edit_user_profile.html', {
        'form': form,
        'user_profile': user_profile,
         'active_page': 'user_profile_list',
         'notifications':notifications
    })
def check_username(request):
    username = request.GET.get('username')
    exists = User.objects.filter(username=username).exists()
    return JsonResponse({'exists': exists})

# @login_required()
# def dashboard(request):
#     notifications = get_notifications(request.user)

#     context = {
#     'active_page': 'dashboard', 'notifications':notifications}
    
#     return render(request, 'dashboard.html', context)

# @login_required()
# def equipment(request):
#     return render(request, 'equipment.html')

def accept_maintenance(request, maintenance_id):
    maintenance = MaintenanceRecord.objects.get(id=maintenance_id)
    if request.user in maintenance.assigned_technicians.all():
        maintenance.status = 'Accepted'
        maintenance.accepted_by = request.user
        maintenance.save()
        messages.success(request, 'Maintenance task accepted.')
    else:
        messages.error(request, 'You are not assigned to this task.')
    return redirect('maintenance_list')

def complete_maintenance(request, maintenance_id):
    maintenance = MaintenanceRecord.objects.get(id=maintenance_id)
    if request.user in maintenance.assigned_technicians.all():
        maintenance.status = 'Complete'
        maintenance.save()
        messages.success(request, 'Maintenance task marked as complete.')
        
        maintenance_branch = maintenance.branch
        
        # Find the MD Manager in the same branch
        manager = User.objects.filter(userprofile__branch=maintenance_branch, userprofile__role='MD manager').first()
        if manager:
            # Create a notification for the MD Manager
            Notification.objects.create(
                user=manager,
                type = "maintenance",
                message=f'The maintenance task for {maintenance.equipment.name} has been marked as complete.',
            )
        
    else:
        messages.error(request, 'You are not assigned to this task.')
    return redirect('maintenance_list')

def approve_maintenance(request, maintenance_id):
    maintenance = MaintenanceRecord.objects.get(id=maintenance_id)
    if request.user.userprofile.role == 'MD manager':
        maintenance.status = 'Approved'
        maintenance.approved_by = request.user
        maintenance.save()

        # Update equipment's last and next maintenance dates
        equipment = maintenance.equipment
        equipment.last_maintenance_date = timezone.now().date()
        equipment.next_maintenance_date = calculate_next_maintenance_date(equipment)
        equipment.save()

        messages.success(request, 'Maintenance task approved.')
    else:
        messages.error(request, 'You are not authorized to approve this task.')
    return redirect('maintenance_list')

def calculate_next_maintenance_date(equipment):
    from datetime import timedelta
    next_date = equipment.last_maintenance_date
    next_date += timedelta(days=equipment.maintenance_interval_days)
    next_date += timedelta(weeks=equipment.maintenance_interval_weeks)
    next_date += timedelta(days=30 * equipment.maintenance_interval_months)
    next_date += timedelta(days=365 * equipment.maintenance_interval_years)
    return next_date

def mark_notification_as_read(request, notification_id):
    if request.user.is_authenticated:
        try:
            notification = Notification.objects.get(id=notification_id, user=request.user)
            notification.is_read = True
            notification.save()
            # Redirect based on the type of notification
            if notification.type == 'maintenance':  # Assuming you have a 'type' field
                return redirect('maintenance_list')  # Adjust the URL name as necessary
            elif notification.type == 'work_order':
                return redirect('work_order_list')  # Adjust the URL name as necessary
            elif notification.type == 'low_maintenance':
                return redirect('low_maintenance')  # Adjust the URL name as necessary
            elif notification.type == 'low_spare_part':
                return redirect('low_spare_part')  # Adjust the URL name as necessary
            
        except Notification.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Notification not found'})
    return JsonResponse({'status': 'error', 'message': 'User not authenticated'})


def accept_work_order(request, work_order_id):
    
    work_order = get_object_or_404(WorkOrder, id=work_order_id)
    if request.user.userprofile.role == 'MD manager':
        work_order.status = 'Accepted'
        work_order.accepted_by = request.user
        work_order.save()
        messages.success(request, 'Work order accepted.')
    else:
        messages.error(request, 'You are not assigned to this work order.')
    return redirect('work_order_list')

#---------------------------------------------------------------------------



#----------------------------------------------------------------------------

def complete_work_order(request, work_order_id):
    work_order = get_object_or_404(WorkOrder, id=work_order_id)
    
    if request.user in work_order.assigned_technicians.all():
        work_order.status = 'Complete'
        work_order.save()
        
        equipment = work_order.equipment
        equipment.last_maintenance_date = timezone.now().date()
        equipment.next_maintenance_date = calculate_next_maintenance_date(equipment)
        equipment.save()
        messages.success(request, 'Work order marked as complete.')
        
        work_order_branch = work_order.branch
        
        # Find the MD Manager in the same branch
        manager = User.objects.filter(userprofile__branch=work_order_branch, userprofile__role='MD manager').first()
        client = work_order.requester
        if manager:
            # Create a notification for the MD Manager
            Notification.objects.create(
                user=manager,
                message=f'The work order for {work_order.equipment.name} has been marked as complete.',
            )
        if client:
             Notification.objects.create(
                user=client,
                type = "maintenance",
                message=f'The work order for {work_order.equipment.name} has been marked as complete.',
            )
            
    else:
        messages.error(request, 'You are not assigned to this work order.')
    
    return redirect('work_order_list')

def approve_work_order(request, work_order_id):
    work_order = get_object_or_404(WorkOrder, id=work_order_id)
    client = work_order.requester
    
    if request.user == client:
        work_order.status = 'Approved'
        work_order.approved_by = request.user
        work_order.save()

        # Update equipment's last and next maintenance dates if relevant
        

        messages.success(request, 'Work order approved.')
    else:
        messages.error(request, 'You are not authorized to approve this work order.')
    
    return redirect('work_order_list')




def dashboard(request):
    notifications = get_notifications(request.user)

    user = request.user
    user_role = user.userprofile.role
    user_branch = user.userprofile.branch

    context = {
        'active_page': 'dashboard',
        'user_role': user_role,
        'user_branch': user_branch,
        'notifications':notifications,
        


    }

    # Common data for all roles
    today = datetime.now().date()
    last_week = today - timedelta(days=7)

    # Role-specific data
    if user_role in ['MD manager', 'TEC']:
        # Equipment count for the user's branch
        equipment_count = Equipment.objects.filter(branch=user_branch).count()

        # Maintenance records not completed for the user's branch
        maintenance_count = MaintenanceRecord.objects.filter(
            branch=user_branch
        ).exclude(status='Complete').count()

        # Work orders not completed for the user's branch
        work_order_count = WorkOrder.objects.filter(
            branch=user_branch
        ).exclude(status='Complete').count()

        # Maintenance and work orders completed in the last week (for graph)
        maintenance_completed = MaintenanceRecord.objects.filter(
            branch=user_branch,
            status='Complete',
            # completion_date__gte=last_week
        ).count()

        work_order_completed = WorkOrder.objects.filter(
            branch=user_branch,
            status='Complete',
            # completion_date__gte=last_week
        ).count()

        # Recent actions for the user
        recent_actions = MaintenanceRecord.objects.filter(
            assigned_technicians=user)
        # .order_by('-created_at')[:5]

        context.update({
            'equipment_count': equipment_count,
            'maintenance_count': maintenance_count,
            'work_order_count': work_order_count,
            'maintenance_completed': maintenance_completed,
            'work_order_completed': work_order_completed,
            'recent_actions': recent_actions,
        })

    elif user_role == 'MO':
        # Data for all branches
        equipment_count = Equipment.objects.count()
        maintenance_count = MaintenanceRecord.objects.exclude(status='Complete').count()
        work_order_count = WorkOrder.objects.exclude(status='Complete').count()

        maintenance_completed = MaintenanceRecord.objects.filter(
            status='Complete',
            completion_date__gte=last_week
        ).count()

        work_order_completed = WorkOrder.objects.filter(
            status='Complete',
            completion_date__gte=last_week
        ).count()

        # Recent actions for all branches
        recent_actions = MaintenanceRecord.objects.order_by('-created_at')[:5]

        context.update({
            'equipment_count': equipment_count,
            'maintenance_count': maintenance_count,
            'work_order_count': work_order_count,
            'maintenance_completed': maintenance_completed,
            'work_order_completed': work_order_completed,
            'recent_actions': recent_actions,
        })

    elif user_role == 'CL':
        # Work orders added by the client
        work_orders = WorkOrder.objects.filter(requester=user)
        work_order_count = work_orders.count()
        completed_work_orders = work_orders.filter(status='Complete').count()

        context.update({
            'work_order_count': work_order_count,
            'completed_work_orders': completed_work_orders,
            'work_orders': work_orders,
        })

    elif user_role == 'AD':
        # System-wide statistics
        user_count = User.objects.count()
        equipment_count = Equipment.objects.count()
        branch_count = User.objects.values('userprofile__branch').distinct().count()

        context.update({
            'user_count': user_count,
            'equipment_count': equipment_count,
            'branch_count': branch_count,
        })

    return render(request, 'dashboard.html', context)

def check_low_spare_parts(spare_part):
    """
    Check if the spare part quantity is below 5 and create a notification for the MD manager.
    """
    if spare_part.quantity < 5:
        # Get the MD manager of the same branch
        md_manager = User.objects.filter(
            userprofile__branch=spare_part.branch,
            userprofile__role='MD manager'
        ).first()

        if md_manager:
            # Create a notification for the MD manager
            Notification.objects.create(
                user=md_manager,
                type="low_spare_part",
                message=f'Low stock alert: {spare_part.name} is below 5 in {spare_part.branch.name}.',
            )

def low_spare_part(request):
    # Get the user's branch
    user_branch = request.user.userprofile.branch

    # Fetch spare parts with quantity below 5 for the user's branch
    spare_parts = SparePart.objects.filter(branch=user_branch, quantity__lt=5)  # Changed variable name to match template

    # Get notifications for the user
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-timestamp')[:10]

    context = {
        'spare_parts': spare_parts,  # Changed variable name to match template
        'active_page': 'low_spare_part',
        'notifications': notifications,
    }

    return render(request, 'low_spare_part.html', context)



def restock_spare_part(request):
    notifications = get_notifications(request.user)

    if request.method == 'POST':
        selected_spare_part_id = request.POST.get('spare_part')  # Get the selected spare part ID
        spare_part = get_object_or_404(SparePart, id=selected_spare_part_id)  # Fetch the spare part instance

        form = RestockSparePartForm(request.POST, request.FILES)
        if form.is_valid():
            restock = form.save(commit=False)
            restock.spare_part = spare_part  # Associate the restock with the spare part
            restock.restock_date = timezone.now()  # Set the restock date to the current time
            restock.save()

            # Update the spare part quantity and last_restock_date
            spare_part.quantity += restock.quantity
            spare_part.last_restock_date = restock.restock_date
            spare_part.save()

            messages.success(request, f'{restock.quantity} units of {spare_part.name} restocked successfully!')
            return redirect('spare_part_list')
    else:
        form = RestockSparePartForm()

    # Pass a list of spare parts to the template
    user_branch = request.user.userprofile.branch
    spare_parts = SparePart.objects.filter(branch=user_branch)

    context = {
        'form': form,
        'spare_parts': spare_parts,  # Ensure you pass all spare parts to the template
        'active_page': 'spare_part_list',
        'notifications': notifications,
    }
    return render(request, 'restock_spare_part.html', context)
def restock_list(request):
    # Get the user's branch
    user_branch = request.user.userprofile.branch

    # Fetch restock records for spare parts in the user's branch
    restock_list = RestockSparePart.objects.filter(spare_part__branch=user_branch).order_by('-restock_date')

    # Get notifications for the user
    notifications = get_notifications(request.user)

    context = {
        'restock_list': restock_list,
        'active_page': 'restock_list',
        'notifications': notifications,
        'title': 'Restock List',
    }

    return render(request, 'restock_list.html', context)


def restock_spare_part_page(request):
    notifications = get_notifications(request.user)

    user_branch = request.user.userprofile.branch

    context = {
        'spare_parts': SparePart.objects.filter(branch=user_branch),  # Fetch spare parts for the branch
        'active_page': 'spare_part_list',
        'notifications': notifications,
    }

    return render(request, 'restock_spare_part.html', context)


# def maintenance_due(request):
#     notifications = get_notifications(request.user)

#     return render(request,'maintenance_due.html', {'active_page':'maintenance_due','notifications':notifications})

# def maintenance_due(request):
#     user_branch = request.user.branch
#     today = timezone.now().date()
#     due_date = today + timedelta(days=5)

#     due_equipment = Equipment.objects.filter(
#         branch=user_branch,
#         next_maintenance_date__lte=due_date,
#         next_maintenance_date__gte=today
#     )

#     # Notify MD managers in the same branch
#     md_managers = User.objects.filter(
#         branch=user_branch,
#         role__in=['MD manager', 'Maintenance Department Manager']
#     )

#     for manager in md_managers:
#         messages.warning(
#             request,
#             f"Equipment {equipment.name} is due for maintenance on {equipment.next_maintenance_date}."
#         )

#     return render(request, 'maintenance_due.html', {'due_equipment': due_equipment})
