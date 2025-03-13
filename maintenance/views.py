from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.http import Http404
from datetime import datetime
from django.db.models import Count, Q, Sum
from datetime import datetime, timedelta 
from django.utils import timezone
from django.http import JsonResponse
from django.urls import reverse
from django.db.models.deletion import ProtectedError, Collector
from django.views.decorators.csrf import csrf_exempt

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.units import inch
from docx.shared import Pt
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from reportlab.lib.styles import ParagraphStyle


import io

import json
from import_export import resources
from import_export.formats import base_formats
from import_export.admin import ImportMixin, ExportMixin
from .models import MaintenanceRecord, MaintenanceTask, Manufacturer, SparePart, SparePartUsage, RestockSparePart, DecommissionedEquipment,Equipment, Notification,WorkOrder,Branch,UserProfile, Task, TaskGroup, TaskCompletion

from .forms import EquipmentForm, SparePartForm, MaintenanceRecordForm, ManufacturerForm, WorkOrderForm, SparePartUsageForm, DecommissionedEquipmentForm, MaintenanceTaskForm,  RestockSparePartForm, BranchForm, UserProfileForm, TaskForm, TaskGroupForm
from .resources import EquipmentResource
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User


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
            if (request.user.userprofile.role in 'MD manager, TEC'):
                return redirect('maintenance_dashboard')
            elif (request.user.userprofile.role in 'MO'):
                return redirect('maintenance_oversight_dashboard')
            elif (request.user.userprofile.role in 'AD'):
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

def get_notifications(user):
    return Notification.objects.filter(user=user, is_read=False).order_by('-timestamp')[:10]



def manufacturer_list(request):
    user_branch = request.user.userprofile.branch
    
    
    if request.user.userprofile.role in ['MO', 'Maintenance Oversight']:
         manufacturers = Manufacturer.objects.all()  
    else:
        manufacturers = Manufacturer.objects.filter(site = user_branch)
        
    notifications = get_notifications(request.user)

    context = {
        'active_page': 'manufacturer_list',
        'title': 'Manufacturers',
        'item_list': manufacturers,
        'edit_url': 'edit_manufacturer',
        'delete_url': 'delete_manufacturer',
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


def delete_manufacturer(request, id):
    manufacturer = get_object_or_404(Equipment, id=id)
    notifications = get_notifications(request.user)

    
    if request.method == 'POST':
        try:
            manufacturer.delete()
            messages.success(request, 'The manufacturer was deleted successfully.')
            return redirect(reverse('manufacturer_list'))
        except ProtectedError as e:
            messages.error(request, 'This equipment cannot be deleted because it is referenced by other objects.')
            return render(request, 'confirm_delete_protected.html', {
                'object': manufacturer,
                'protected_objects': e.protected_objects,
                'model_name': 'Manufacturer',  # Dynamic model name
                'active_page':'manufacturer_list',
                'notifications':notifications
            })
    
    return render(request, 'confirm_delete.html', {
        'object': manufacturer,
        'model_name': 'Manufacturer',  # Dynamic model name
        'active_page':'manufacturer_list',

        'notifications':notifications

    })


#----------------------------------------------------------------------------------

def work_order_list(request):
    user_branch = request.user.userprofile.branch
    
    if request.user.userprofile.role in ['MO', 'Maintenance Oversight']:
         work_orders = WorkOrder.objects.all()  # Show all equipment for MO
    else:
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
        location = request.POST.get('location')
        description = request.POST.get('description')
        status = 'Pending'  # Default status
        if(request.user.userprofile.role == 'MD manager'):
            status = 'Accepted'

        if not branch or not description:
            messages.error(request, 'Please fill out all required fields.')
            return redirect('add_work_order_page')

        try:
            work_order = WorkOrder.objects.create(
                requester=request.user,
                branch_id=branch,
                equipment_id=equipment_id,
                location = location,
                description=description,
                status=status
            )
            messages.success(request, 'Work Order added successfully!')

            # Send notification to the MD Manager of the same branch
            manager = User.objects.filter(userprofile__branch=branch, userprofile__role='MD manager').first()
            if manager:
                Notification.objects.create(
                    user=manager,
                    type = "work_order",
                    message=f'New work order: {work_order.location}.',
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
    equipments = Equipment.objects.filter(branch=user_branch)

    if request.method == 'POST':
        # Get form data
        equipment_id = request.POST.get('equipment')
        assigned_technicians = request.POST.getlist('assigned_technicians[]')
        spare_parts_post = request.POST.getlist('spare_parts[]')
        spare_part_quantities = request.POST.getlist('spare_part_quantities[]')

        try:
            # Step 1: Update the equipment
            if equipment_id:
                equipment = Equipment.objects.get(id=equipment_id)
                work_order.equipment = equipment
                work_order.save()

            # Step 2: Update assigned technicians (only for MD manager)
            if request.user.userprofile.role == 'MD manager':
                work_order.assigned_technicians.set(assigned_technicians)

            # Step 3: Add back the old quantities to the spare parts
            spare_part_usages = SparePartUsage.objects.filter(work_order=work_order)
            for usage in spare_part_usages:
                spare_part = usage.spare_part
                spare_part.quantity += usage.quantity_used
                spare_part.save()

            # Step 4: Process the new spare parts and quantities (only for Technician and if not approved)
            if request.user.userprofile.role == 'TEC' and work_order.status != 'Approved':
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
                        work_order=work_order,
                        spare_part=spare_part,
                        defaults={'quantity_used': quantity_used},
                    )

                # Step 5: Delete any remaining spare part usages that were not in the form
                SparePartUsage.objects.filter(work_order=work_order).exclude(
                    spare_part_id__in=[int(id) for id in spare_parts_post if id.strip()]
                ).delete()

            # Notify assigned technicians
            for technician_id in assigned_technicians:
                technician = User.objects.get(id=technician_id)
                Notification.objects.create(
                    user=technician,
                    type="work_order",
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
        'equipments': equipments,
        'selected_equipment_id': work_order.equipment.id if work_order.equipment else None,
        'spare_part_usages': SparePartUsage.objects.filter(work_order=work_order),
    }
    return render(request, 'edit_work_order.html', context)
#------------------------------------------------------------------------------------



def spare_part_usage_list(request):
    notifications = get_notifications(request.user)
    user_branch = request.user.userprofile.branch
    
    if request.user.userprofile.role in ['MO', 'Maintenance Oversight']:
         spare_part_usages = SparePartUsage.objects.all()
    else:
        spare_part_usages = SparePartUsage.objects.filter(
    Q(maintenance_record__branch=user_branch) | Q(work_order__branch=user_branch)
     )
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
    user_branch = request.user.userprofile.branch
    if request.user.userprofile.role in ['MO', 'Maintenance Oversight']:
        decommissioned_equipments = DecommissionedEquipment.objects.all()  # Show all equipment for MO
    else:
        decommissioned_equipments = DecommissionedEquipment.objects.filter(branch=user_branch)
    
    
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
def maintenance_task_list(request):
    user_branch = request.user.userprofile.branch
    notifications = get_notifications(request.user)


    maintenance_tasks = MaintenanceTask.objects.all()
    context = {
        'active_page': 'maintenance_task_list',
        'title': 'Maintenance Task',
        'item_list': maintenance_tasks,
        'edit_url': 'edit_maintenance_task',
        'delete_url':'delete_maintenance_task',
        'notifications':notifications
    }
    return render(request, 'maintenance_task_list.html', context)

def add_maintenance_task_page(request):
    user_branch = request.user.userprofile.branch
    notifications = get_notifications(request.user)


    return render(request, 'add_maintenance_task.html',{ 'active_page': 'maintenance_task_list', 'notifications':notifications
})



def add_maintenance_task(request):
    user_branch = request.user.userprofile.branch
    notifications = get_notifications(request.user)

    if request.method == 'POST':
        maintenance_task_form = MaintenanceTaskForm(request.POST)
        if maintenance_task_form.is_valid():
            maintenance_task = maintenance_task_form.save()

            frequencies = ['daily', 'weekly', 'monthly', 'biannual', 'annual']
            for frequency in frequencies:
                task_descriptions = request.POST.getlist(f'{frequency}_tasks[]')
                if task_descriptions:
                    task_group = TaskGroup.objects.create(maintenance_task=maintenance_task, frequency=frequency)
                    for description in task_descriptions:
                        Task.objects.create(task_group=task_group, description=description)

            messages.success(request, 'Maintenance Task and associated tasks added successfully!')
            return redirect('maintenance_task_list')
    else:
        maintenance_task_form = MaintenanceTaskForm()

    return render(request, 'add_maintenance_task.html', {
        'active_page': 'maintenance_task_list',
        'branch': user_branch,
        'notifications': notifications,
        'maintenance_task_form': maintenance_task_form,
        'frequencies': ['daily', 'weekly', 'monthly', 'biannual', 'annual'],
    })
def edit_maintenance_task(request, id):
    user_branch = request.user.userprofile.branch
    notifications = get_notifications(request.user)
    maintenance_task = get_object_or_404(MaintenanceTask, id=id)

    if request.method == 'POST':
        form = MaintenanceTaskForm(request.POST, instance=maintenance_task)
        if form.is_valid():
            maintenance_task = form.save()

            # Update tasks for each frequency
            frequencies = ['daily', 'weekly', 'monthly', 'biannual', 'annual']
            for frequency in frequencies:
                task_descriptions = request.POST.getlist(f'{frequency}_tasks[]')
                task_group, created = TaskGroup.objects.get_or_create(
                    maintenance_task=maintenance_task,
                    frequency=frequency
                )

                # Get existing tasks for this frequency
                existing_tasks = task_group.tasks.all()

                # Update or create tasks
                new_tasks = []
                for description in task_descriptions:
                    if description.strip():  # Ignore empty tasks
                        # Check if a task with this description already exists
                        task = existing_tasks.filter(description=description).first()
                        if not task:
                            # Create a new task if it doesn't exist
                            task = Task.objects.create(task_group=task_group, description=description)
                        new_tasks.append(task)

                # Delete tasks that are no longer needed
                tasks_to_delete = existing_tasks.exclude(id__in=[task.id for task in new_tasks])
                tasks_to_delete.delete()

            messages.success(request, 'Maintenance Task updated successfully!')
            return redirect('maintenance_task_list')
    else:
        form = MaintenanceTaskForm(instance=maintenance_task)

    # Preprocess tasks for each frequency
    frequencies = ['daily', 'weekly', 'monthly', 'biannual', 'annual']
    task_groups = {}
    for frequency in frequencies:
        task_group = maintenance_task.task_groups.filter(frequency=frequency).first()
        if task_group:
            task_groups[frequency] = task_group.tasks.all()
        else:
            task_groups[frequency] = []

    return render(request, 'edit_maintenance_task.html', {
        'form': form,
        'maintenance_task': maintenance_task,
        'frequencies': frequencies,
        'task_groups': task_groups,
        'active_page': 'maintenance_task_list',
        'notifications': notifications,
    })
def delete_maintenance_task(request, id):
    # Fetch the MaintenanceTask instance or return a 404 error if not found
    maintenancetask = get_object_or_404(MaintenanceTask, id=id)
    notifications = get_notifications(request.user)
    
    if request.method == 'POST':
        # Check if any Equipment objects reference this MaintenanceTask's equipment_type
        related_equipment = Equipment.objects.filter(equipment_type=maintenancetask.equipment_type)
        
        if related_equipment.exists():
            # If there are related Equipment objects, render the protected page
            messages.error(request, 'This maintenance task cannot be deleted because there are equipments with this type of maitnenance task.')
            return render(request, 'confirm_delete_protected.html', {
                'active_page': 'maintenance_task_list',
                'object': maintenancetask,
                'protected_objects': related_equipment,  # Pass the related Equipment objects
                'model_name': 'Maintenance Task',  # Dynamic model name
                'notifications': notifications,
            })
        
        # If no related Equipment objects, delete the MaintenanceTask
        maintenancetask.delete()
        messages.success(request, 'The maintenance task was deleted successfully.')
        return redirect(reverse('maintenance_task_list'))  # Redirect to the list view
    
    # If it's a GET request, render the confirmation page
    return render(request, 'confirm_delete.html', {
        'active_page': 'maintenance_task_list',
        'object': maintenancetask,
        'model_name': 'Maintenance Task',  # Dynamic model name
        'notifications': notifications,
    })
#-----------------------------------------------------------------add task for frequency----------------------------------------


def add_tasks_for_frequency(request, frequency):
    user_branch = request.user.userprofile.branch
    notifications = get_notifications(request.user)

    if request.method == 'POST':
        # Get the maintenance task ID from the form (assuming it's passed as a hidden field)
        maintenance_task_id = request.POST.get('maintenance_task_id')
        if not maintenance_task_id:
            messages.error(request, 'Maintenance Task ID is missing.')
            return redirect('add_maintenance_task')

        # Fetch the maintenance task
        try:
            maintenance_task = MaintenanceTask.objects.get(id=maintenance_task_id)
        except MaintenanceTask.DoesNotExist:
            messages.error(request, 'Invalid Maintenance Task.')
            return redirect('add_maintenance_task')

        # Create or fetch the TaskGroup for the given frequency
        task_group, created = TaskGroup.objects.get_or_create(
            maintenance_task=maintenance_task,
            frequency=frequency
        )

        # Get the list of tasks from the form
        task_descriptions = request.POST.getlist('tasks[]')
        if not task_descriptions:
            messages.error(request, 'No tasks provided.')
            return redirect('add_maintenance_task')

        # Save each task
        for description in task_descriptions:
            Task.objects.create(task_group=task_group, description=description)

        messages.success(request, f'{frequency.capitalize()} tasks added successfully!')
        return redirect('add_maintenance_task')

    else:
        # Render the form for adding tasks
        maintenance_task_form = MaintenanceTaskForm()
        task_form = TaskForm()

    return render(request, 'add_tasks_for_frequency.html', {
        'active_page': 'maintenance_task_list',
        'branch': user_branch,
        'notifications': notifications,
        'maintenance_task_form': maintenance_task_form,
        'task_form': task_form,
        'frequency': frequency,
    })


@csrf_exempt
def add_task(request, frequency):
    if request.method == 'POST':
        data = json.loads(request.body)
        description = data.get('description')

        # Fetch the maintenance task (you may need to pass the ID in the request)
        maintenance_task = MaintenanceTask.objects.get(id=1)  # Replace with your logic

        # Create or fetch the TaskGroup
        task_group, created = TaskGroup.objects.get_or_create(
            maintenance_task=maintenance_task,
            frequency=frequency
        )

        # Create the task
        Task.objects.create(task_group=task_group, description=description)

        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@csrf_exempt
def delete_task(request, task_id):
    if request.method == 'POST':
        task = Task.objects.get(id=task_id)
        task.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})
#--------------------------------------------------------------------------------------------



def equipment_list(request):
    user_branch = request.user.userprofile.branch
    notifications = get_notifications(request.user)

    # Fetch all branches for the branch filter (only for Maintenance Oversight)
    branches = Branch.objects.all()

    # Fetch all equipment types from the MaintenanceTask model
    equipment_types = MaintenanceTask.objects.values_list('equipment_type', flat=True).distinct()

    # Filter equipment based on user role
    if request.user.userprofile.role in ['MO', 'Maintenance Oversight']:
        equipments = Equipment.objects.all()  # Show all equipment for MO
    else:
        equipments = Equipment.objects.filter(branch=user_branch)  # Filter by branch for other roles

    context = {
        'active_page': 'equipment_list',
        'title': 'Equipments',
        'item_list': equipments,
        'edit_url': 'edit_equipment',
        'delete_url': 'delete_equipment',
        'notifications': notifications,
        'branches': branches,
        'equipment_types': equipment_types,
    }
    return render(request, 'equipment_list.html', context)
def add_equipment_page(request):
    notifications = get_notifications(request.user)
    user_branch = request.user.userprofile.branch

    # Fetch unique equipment types from MaintenanceTask
    equipment_types = MaintenanceTask.objects.values_list('equipment_type', flat=True).distinct()

    manufacturers = Manufacturer.objects.filter(site=user_branch)
    branch = user_branch
    return render(request, 'equipment.html', {
        'manufacturers': manufacturers,
        'branch': branch,
        'equipment_types': equipment_types,  # Pass equipment types to the template
        'active_page': 'equipment_list',
        'notifications': notifications
    })


def add_equipment(request):
    notifications = get_notifications(request.user)
    user_branch = request.user.userprofile.branch
    manufacturers = Manufacturer.objects.filter(site=user_branch)

    # Fetch unique equipment types from MaintenanceTask
    equipment_types = MaintenanceTask.objects.values_list('equipment_type', flat=True).distinct()

    if request.method == 'POST':
        # Get form data
        name = request.POST.get('name')
        equipment_type = request.POST.get('equipment_type')
        manufacturer_id = request.POST.get('manufacturer')
        model_number = request.POST.get('model_number')
        serial_number = request.POST.get('serial_number')
        location = request.POST.get('location')
        installation_date = request.POST.get('installation_date')
        # maintenance_interval_years = request.POST.get('maintenance_interval_years', '0')
        # maintenance_interval_months = request.POST.get('maintenance_interval_months', '0')
        # maintenance_interval_weeks = request.POST.get('maintenance_interval_weeks', '0')
        # maintenance_interval_days = request.POST.get('maintenance_interval_days', '0')
        status = request.POST.get('status')
        remark = request.POST.get('remark')

        # Validate required fields
        if not name or not equipment_type or not manufacturer_id or not model_number or not serial_number or not location or not installation_date or not status:
            messages.error(request, 'Please fill out all required fields.')
            context = {
                'manufacturers': manufacturers,
                'branch': user_branch,
                'equipment_types': equipment_types,  # Pass equipment types to the template
                'active_page': 'equipment_list',
                'notifications': notifications
            }
            return render(request, 'equipment.html', context)

        try:
            # Convert dates from string to date objects
            installation_date = datetime.strptime(installation_date, '%Y-%m-%d').date()

            # Convert maintenance intervals to integers
            # maintenance_interval_years = int(maintenance_interval_years)
            # maintenance_interval_months = int(maintenance_interval_months)
            # maintenance_interval_weeks = int(maintenance_interval_weeks)
            # maintenance_interval_days = int(maintenance_interval_days)

            # Create and save the Equipment object
            Equipment.objects.create(
                name=name,
                equipment_type=equipment_type,
                manufacturer_id=manufacturer_id,
                model_number=model_number,
                serial_number=serial_number,
                branch=user_branch,
                location=location,
                installation_date=installation_date,
                # maintenance_interval_years=maintenance_interval_years,
                # maintenance_interval_months=maintenance_interval_months,
                # maintenance_interval_weeks=maintenance_interval_weeks,
                # maintenance_interval_days=maintenance_interval_days,
                status=status,
                remark=remark
            )
            messages.success(request, 'Equipment added successfully!')
            return redirect('equipment_list')
        except ValueError as e:
            messages.error(request, f'Invalid date format: {str(e)}')
            context = {
                'manufacturers': manufacturers,
                'branch': user_branch,
                'equipment_types': equipment_types,  # Pass equipment types to the template
                'active_page': 'equipment_list',
                'notifications': notifications
            }
            return render(request, 'equipment.html', context)
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            context = {
                'manufacturers': manufacturers,
                'branch': user_branch,
                'equipment_types': equipment_types,  # Pass equipment types to the template
                'active_page': 'equipment_list',
                'notifications': notifications
            }
            return render(request, 'equipment.html', context)

    # For GET requests, render the form with manufacturers and the user's branch
    context = {
        'manufacturers': manufacturers,
        'branch': user_branch,
        'equipment_types': equipment_types,  # Pass equipment types to the template
        'active_page': 'equipment_list',
        'notifications': notifications
    }
    return render(request, 'equipment.html', context)
def edit_equipment(request, id):
    notifications = get_notifications(request.user)
    equipment = get_object_or_404(Equipment, id=id)

    # Fetch unique equipment types from MaintenanceTask
    equipment_types = MaintenanceTask.objects.values_list('equipment_type', flat=True).distinct()

    if request.method == 'POST':
        form = EquipmentForm(request.POST, instance=equipment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Equipment changed successfully')
            return redirect('equipment_list')
    else:
        form = EquipmentForm(instance=equipment)

    return render(request, 'edit_equipment.html', {
        'form': form,
        'equipment': equipment,
        'equipment_types': equipment_types,  # Pass equipment types to the template
        'active_page': 'equipment_list',
        'notifications': notifications
    })

def delete_equipment(request, id):
    equipment = get_object_or_404(Equipment, id=id)
    notifications = get_notifications(request.user)

    
    if request.method == 'POST':
        try:
            equipment.delete()
            messages.success(request, 'The equipment was deleted successfully.')
            return redirect(reverse('equipment_list'))
        except ProtectedError as e:
            messages.error(request, 'This equipment cannot be deleted because it is referenced by other objects.')
            return render(request, 'confirm_delete_protected.html', {
                'object': equipment,
                'protected_objects': e.protected_objects,
                'model_name': 'Equipment',  # Dynamic model name
                'active_page':'equipment_list',
                'notifications':notifications
            })
    
    return render(request, 'confirm_delete.html', {
        'object': equipment,
        'model_name': 'Equipment',  # Dynamic model name
        'active_page':'equipment_list',

        'notifications':notifications

    })

#-----------------------------------------------------------------------------------------------

def spare_part_list(request):
    notifications = get_notifications(request.user)

    user_branch = request.user.userprofile.branch
    
    if request.user.userprofile.role in ['MO', 'Maintenance Oversight']:
         spare_parts = SparePart.objects.all()
    else:
        spare_parts = SparePart.objects.filter(branch = user_branch)
        

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


 #-----------------------------------------------maintenance-----------------------------------------------------------
    
        

    

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
        'maintenance_tasks': MaintenanceTask.objects.all(),
        'work_orders': WorkOrder.objects.filter(branch=user_branch),
        'spare_parts': SparePart.objects.filter(branch=user_branch),
        'active_page': 'maintenance_list',
        'notifications':notifications
    }
    return render(request, 'add_maintenance.html', context)

def add_maintenance(request):
    user_branch = request.user.userprofile.branch
    notifications = get_notifications(request.user)

    context = {
        'equipments': Equipment.objects.filter(branch=user_branch),
        'technicians': User.objects.filter(userprofile__branch=user_branch, userprofile__role='TEC'),
        'branch': user_branch,
        'maintenance_tasks': MaintenanceTask.objects.all(),
        'work_orders': WorkOrder.objects.filter(branch=user_branch),
        'spare_parts': SparePart.objects.filter(branch=user_branch),
        'active_page': 'maintenance_list',
        'notifications': notifications,
    }

    if request.method == 'POST':
        equipment_id = request.POST.get('equipment')
        assigned_technicians = request.POST.getlist('assigned_technicians[]')
        branch_id = request.POST.get('branch')
        maintenance_type = request.POST.get('maintenance_type')  # Ensure this matches the form field name
        spare_parts = request.POST.getlist('spare_parts[]')
        spare_part_quantities = request.POST.getlist('spare_part_quantities[]')
        remark = request.POST.get('remark')
        procedure = request.POST.get('procedure')
        problems = request.POST.get('problems')
        status = request.POST.get('status')

        try:
            # Step 1: Get the selected equipment
            equipment = Equipment.objects.get(id=equipment_id)

            # Step 2: Get the equipment_type from the selected equipment
            equipment_type = equipment.equipment_type

            # Step 3: Fetch the maintenance_task associated with the equipment_type
            maintenance_task = MaintenanceTask.objects.filter(equipment_type=equipment_type).first()

            if not maintenance_task:
                messages.error(request, f'No maintenance task found for equipment type: {equipment_type}.')
                return render(request, 'add_maintenance.html', context)

            # Step 4: Create the maintenance record
            maintenance = MaintenanceRecord.objects.create(
                equipment_id=equipment_id,
                branch_id=branch_id,
                maintenance_task=maintenance_task,
                maintenance_type=maintenance_type,  # Ensure this is correctly saved
                remark=remark,
                procedure=procedure,
                problems=problems,
                status='Not Started',
            )
            maintenance.assigned_technicians.set(assigned_technicians)

            # Step 5: Process spare parts
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

            # Step 6: Notify assigned technicians
            for technician_id in assigned_technicians:
                technician = User.objects.get(id=technician_id)
                Notification.objects.create(
                    user=technician,
                    type="maintenance",
                    message=f'You have been assigned a new maintenance task: {maintenance.equipment.name}.',
                )

            messages.success(request, 'Maintenance record added successfully!')
            return redirect('maintenance_list')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return render(request, 'add_maintenance.html', context)

    return render(request, 'add_maintenance.html', context)
def maintenance_list(request):
    notifications = get_notifications(request.user)

    user_branch = request.user.userprofile.branch
    
    # Filter equipment based on user role
    if request.user.userprofile.role in ['MO', 'Maintenance Oversight']:
        maintenance_records = MaintenanceRecord.objects.all()  # Show all equipment for MO
    else:
        maintenance_records = MaintenanceRecord.objects.filter(branch = user_branch ) # Filter by branch for other roles

     # Fetch all maintenance records
    context = {
        'active_page': 'maintenance_list',
        'title': 'Maintenance List',
        'item_list': maintenance_records,
        'edit_url': 'edit_maintenance',  # URL name for editing maintenance records
        'delete_url':'delete_maintenance',
        'notifications':notifications
    }
    return render(request, 'maintenance_list.html', context)
    

def edit_maintenance(request, id):
    notifications = get_notifications(request.user)
    user_branch = request.user.userprofile.branch
    maintenance = get_object_or_404(MaintenanceRecord, id=id)
    spare_parts = SparePart.objects.filter(branch=user_branch)
    spare_part_usages = SparePartUsage.objects.filter(maintenance_record=maintenance)

    # Fetch tasks associated with the maintenance task and maintenance type
    tasks = Task.objects.filter(
        task_group__maintenance_task=maintenance.maintenance_task,
        task_group__frequency=maintenance.maintenance_type
    )
    completed_task_ids = maintenance.completed_tasks.values_list('id', flat=True)
    
    if request.method == 'POST':
        if request.user in maintenance.assigned_technicians.all():
            # Get form data
            equipment_id = request.POST.get('equipment')
            assigned_technicians = request.POST.getlist('assigned_technicians')
            branch_id = request.POST.get('branch')
            maintenance_type = request.POST.get('maintenance_type')  # e.g., daily, weekly
            spare_parts_post = request.POST.getlist('spare_parts[]')
            spare_part_quantities = request.POST.getlist('spare_part_quantities[]')
            remark = request.POST.get('remark')
            procedure = request.POST.get('procedure')
            problems = request.POST.get('problems')
            status = request.POST.get('status')
            completed_tasks = request.POST.getlist('completed_tasks')  # Get completed tasks

            try:
                # Step 1: Get the selected equipment
                equipment = Equipment.objects.get(id=equipment_id)

                # Step 2: Get the equipment_type from the selected equipment
                equipment_type = equipment.equipment_type

                # Step 3: Fetch the maintenance_task associated with the equipment_type
                maintenance_task = MaintenanceTask.objects.filter(equipment_type=equipment_type).first()

                if not maintenance_task:
                    messages.error(request, f'No maintenance task found for equipment type: {equipment_type}.')
                    return render(request, 'edit_maintenance.html', {
                        'maintenance': maintenance,
                        'spare_parts': spare_parts,
                        'spare_part_usages': spare_part_usages,
                        'tasks': tasks,
                        'completed_task_ids': completed_task_ids,
                        'active_page': 'maintenance_list',
                        'notifications': notifications
                    })

                # Step 4: Update maintenance record
                maintenance.equipment_id = equipment_id
                maintenance.maintenance_task = maintenance_task  # Use the fetched maintenance_task
                maintenance.maintenance_type = maintenance_type  # Update maintenance_type
                maintenance.remark = remark
                maintenance.procedure = procedure
                maintenance.problems = problems
                maintenance.save()

                # Step 5: Add back the old quantities to the spare parts
                for usage in spare_part_usages:
                    spare_part = usage.spare_part
                    spare_part.quantity += usage.quantity_used
                    spare_part.save()

                # Step 6: Process the new spare parts and quantities
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
                            
                        return redirect(f'{request.path}?equipment={equipment_id}&maintenance_task={maintenance_task.id}&error=1')

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

                # Step 7: Delete any remaining spare part usages that were not in the form
                SparePartUsage.objects.filter(maintenance_record=maintenance).exclude(
                    spare_part_id__in=[int(id) for id in spare_parts_post]
                ).delete()

                # Step 8: Update completed tasks
                maintenance.completed_tasks.clear()  # Clear existing completed tasks
                for task_id in completed_tasks:
                    task = Task.objects.get(id=task_id)
                    TaskCompletion.objects.create(
                        maintenance_record=maintenance,
                        task=task,
                        completed_by=request.user
                    )

                messages.success(request, 'Maintenance record updated successfully!')
                return redirect('maintenance_list')
            except Exception as e:
                messages.error(request, f'An error occurred: {str(e)}')
                return render(request, 'edit_maintenance.html', {
                    'maintenance': maintenance,
                    'spare_parts': spare_parts,
                    'spare_part_usages': spare_part_usages,
                    'tasks': tasks,
                    'completed_task_ids': completed_task_ids,
                    'active_page': 'maintenance_list',
                    'notifications': notifications
                })
        else:
            messages.error(request, 'You are not assigned to this task.')
    # For GET requests, pre-fill the form and spare parts
    form = MaintenanceRecordForm(instance=maintenance)
    return render(request, 'edit_maintenance.html', {
        'form': form,
        'maintenance': maintenance,
        'spare_parts': spare_parts,
        'spare_part_usages': spare_part_usages,
        'tasks': tasks,
        'completed_task_ids': completed_task_ids,
        'active_page': 'maintenance_list',
        'notifications': notifications
    })

#------------------------------------------------------------delete maintenance------------------------------------------
def delete_maintenance(request, id):
    # Fetch the MaintenanceRecord instance or return a 404 error if not found
    maintenance_record = get_object_or_404(MaintenanceRecord, id=id)
    notifications = get_notifications(request.user)

    
    if request.method == 'POST':
        # If the user confirms deletion, attempt to delete the record
        try:
            maintenance_record.delete()
            messages.success(request, 'The record was deleted successfully.')
            return redirect(reverse('maintenance_list'))  # Redirect to the list view
        except ProtectedError as e:
            # If there are protected objects, render the protected page
            messages.error(request, 'This record cannot be deleted because it is referenced by other objects.')
            return render(request, 'confirm_delete_protected.html', {
                'object': maintenance_record,
                'protected_objects': e.protected_objects,
                'model_name': 'Maintenance Record',  # Dynamic model name
                'active_page':'maintenance_list',
                'notifications': notifications,


            })
    
    # If it's a GET request, render the confirmation page
    return render(request, 'confirm_delete.html', {
        'object': maintenance_record,
        'model_name': 'Maintenance Record',  # Dynamic model name
        'active_page':'maintenance_list',
        'notifications': notifications

    })
#-------------------------------------------------------------------get_tasks-------------------------------------
def get_tasks(request):
    equipment_id = request.GET.get('equipment_id')
    maintenance_type = request.GET.get('maintenance_type')

    if not equipment_id or not maintenance_type:
        return JsonResponse({'tasks': []})

    try:
        # Get the equipment
        equipment = Equipment.objects.get(id=equipment_id)

        # Get the maintenance task associated with the equipment's type
        maintenance_task = MaintenanceTask.objects.filter(equipment_type=equipment.equipment_type).first()

        if not maintenance_task:
            return JsonResponse({'tasks': []})

        # Get the task group for the selected maintenance type and frequency
        task_group = TaskGroup.objects.filter(
            maintenance_task=maintenance_task,
            frequency=maintenance_type
        ).first()

        if task_group:
            # Fetch tasks associated with the task group
            tasks = task_group.tasks.all()
            tasks_data = [{'id': task.id, 'description': task.description} for task in tasks]
            return JsonResponse({'tasks': tasks_data})
        else:
            return JsonResponse({'tasks': []})
    except Exception as e:
        return JsonResponse({'tasks': []})
#-----------------------------------------------------accept maintenance----------------------------------------


def accept_maintenance(request, maintenance_id):
    # Fetch the MaintenanceRecord instance or return a 404 error if not found
    maintenance = get_object_or_404(MaintenanceRecord, id=maintenance_id)
    
    # Check if the current user is assigned to the maintenance task
    if request.user in maintenance.assigned_technicians.all():
        # Update the status to 'Accepted'
        maintenance.status = 'Accepted'
        
        # Add the current user to the accepted_by ManyToManyField
        maintenance.accepted_by.add(request.user)
        
        # Save the changes
        maintenance.save()
        
        # Display a success message
        messages.success(request, 'Maintenance task accepted.')
    else:
        # Display an error message if the user is not assigned to the task
        messages.error(request, 'You are not assigned to this task.')
    
    # Redirect to the maintenance list page
    return redirect('edit_maintenance',id = maintenance_id)

#--------------------------------------complete maintenance-----------------------------------------------------------

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
    return redirect('edit_maintenance',id = maintenance_id)

#-------------------------------------approve maintenance-----------------------------------------------------

def approve_maintenance(request, maintenance_id):
    maintenance = MaintenanceRecord.objects.get(id=maintenance_id)
    maintenance_type = maintenance.maintenance_type
    if request.user.userprofile.role == 'MD manager':
        maintenance.status = 'Approved'
        maintenance.approved_by = request.user
        maintenance.save()


        # Update equipment's last and next maintenance dates
        if maintenance_type == 'daily':
            equipment = maintenance.equipment
            equipment.last_daily_maintenance_date = timezone.now().date()
            equipment.next_daily_maintenance_date = calculate_next_maintenance_date(maintenance_type)
            equipment.save()
        elif maintenance_type == 'weekly':
            equipment = maintenance.equipment
            equipment.last_weekly_maintenance_date = timezone.now().date()
            equipment.next_weekly_maintenance_date = calculate_next_maintenance_date(maintenance_type)
            equipment.save()
        elif maintenance_type == 'monthly':
            equipment = maintenance.equipment
            equipment.last_monthly_maintenance_date = timezone.now().date()
            equipment.next_monthly_maintenance_date = calculate_next_maintenance_date(maintenance_type)
            equipment.save()
        elif maintenance_type == 'annual':
            equipment = maintenance.equipment
            equipment.last_annual_maintenance_date = timezone.now().date()
            equipment.next_annual_maintenance_date = calculate_next_maintenance_date(maintenance_type)
            equipment.save()
        elif maintenance_type == 'biannual':
            equipment = maintenance.equipment
            equipment.last_biannual_maintenance_date = timezone.now().date()
            equipment.next_biannual_maintenance_date = calculate_next_maintenance_date(maintenance_type)
            equipment.save()

        messages.success(request, 'Maintenance task approved.')
    else:
        messages.error(request, 'You are not authorized to approve this task.')
    return redirect('maintenance_list')

#------------------------------------------------------accept work order------------------------------------

def accept_work_order(request, work_order_id):
    
    work_order = get_object_or_404(WorkOrder, id=work_order_id)
    if request.user.userprofile.role == 'MD manager':
        work_order.status = 'Accepted'
        work_order.accepted_by = request.user
        work_order.save()
        messages.success(request, 'Work order accepted.')
    else:
        messages.error(request, 'You are not assigned to this work order.')
    return redirect('edit_work_order', id=work_order.id)
#------------------------------------------------------reject work order---------------------------------------------
def reject_work_order(request, work_order_id):
    
    work_order = get_object_or_404(WorkOrder, id=work_order_id)
    if request.user.userprofile.role == 'MD manager':
        work_order.status = 'Rejected'
        work_order.rejected_by = request.user
        work_order.save()
        messages.success(request, 'Work order Rejected.')
    else:
        messages.error(request, 'You did not assign this work order.')
    return redirect('edit_work_order', id=work_order.id)

#-------------------------------------------------------complete work order--------------------




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
        # if client:
        #      Notification.objects.create(
        #         user=client,
        #         type = "maintenance",
        #         message=f'The work order for {work_order.equipment.name} has been marked as complete.',
        #     )
            
    else:
        messages.error(request, 'You are not assigned to this work order.')
    
    return redirect('work_order_list')


#-------------------------------------------------------approve work order

def approve_work_order(request, work_order_id):
    work_order = get_object_or_404(WorkOrder, id=work_order_id)
    # manager = work_order.
    
# if request.user == manager:
    work_order.status = 'Approved'
    work_order.approved_by = request.user
    work_order.save()

    # Update equipment's last and next maintenance dates if relevant
    for technician in work_order.assigned_technicians.all():
        Notification.objects.create(
            user= technician,
            type = 'work_order',
            message=f'The work order for {work_order.equipment.name} has been approved by {work_order.approved_by}.',
        )

    messages.success(request, 'Work order approved.')
# else:
#     messages.error(request, 'You are not authorized to approve this work order.')

    return redirect('work_order_list')




#-----------------------------------------calculate next maintenance date--------------------------------------------------

def calculate_next_maintenance_date(maintenance_type):
    """
    Calculate the next maintenance date based on the maintenance type.
    """
    today = timezone.now().date()

    if maintenance_type == 'daily':
        # For daily maintenance, add 1 day
        return today + timedelta(days=1)
    
    elif maintenance_type == 'weekly':
        # For weekly maintenance, add 1 week
        return today + timedelta(weeks=1)
    
    elif maintenance_type == 'monthly':
        # For monthly maintenance, add 1 month (approximated as 30 days)
        return today + timedelta(days=30)
    
    elif maintenance_type == 'annual':
        # For annual maintenance, add 1 year (approximated as 365 days)
        return today + timedelta(days=365)
    
    elif maintenance_type == 'biannual':
        # For biannual maintenance, add 6 months (approximated as 182 days)
        return today + timedelta(days=182)
    
    else:
        # Default fallback: return today + 1 day
        return today + timedelta(days=1)

#-------------------------------------------mark notification as read--------------------------------------------------------

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
            elif notification.type == 'expiration_list':
                return redirect('expired_chemical.html')
            
        except Notification.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Notification not found'})
    return JsonResponse({'status': 'error', 'message': 'User not authenticated'})










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
    
    if request.user.userprofile.role in ['MO', 'Maintenance Oversight']:
        spare_parts = SparePart.objects.filter(quantity__lt=5)

    else:
        spare_parts = SparePart.objects.filter(branch=user_branch, quantity__lt=5)  

    # Fetch spare parts with quantity below 5 for the user's branch

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
    
    if request.user.userprofile.role in ['MO', 'Maintenance Oversight']:
        restock_list = RestockSparePart.objects.all().order_by('-restock_date')

    else:
        restock_list = RestockSparePart.objects.filter(spare_part__branch=user_branch).order_by('-restock_date')

    # Fetch restock records for spare parts in the user's branch

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


def maintenance_due(request):
    notifications = get_notifications(request.user)

    today = timezone.now().date()
    due_in_5_days = today + timezone.timedelta(days=5)

    # Fetch equipment due for maintenance within the next 5 days
    due_equipment = Equipment.objects.filter(
        next_monthly_maintenance_date__lte=due_in_5_days
    ) | Equipment.objects.filter(
        next_biannual_maintenance_date__lte=due_in_5_days
    ) | Equipment.objects.filter(
        next_annual_maintenance_date__lte=due_in_5_days
    )

    # Exclude equipment that has already been maintained (next maintenance date is in the future)
    due_equipment = due_equipment.exclude(
        next_monthly_maintenance_date__gt=today,
        next_biannual_maintenance_date__gt=today,
        next_annual_maintenance_date__gt=today,
    )

    # Role-based filtering
    user_role = request.user.userprofile.role  # Assuming the user's role is stored in a `role` field on the User model
    if user_role in ['MD manager', 'TEC']:  # Manager or Technician
        due_equipment = due_equipment.filter(branch=request.user.userprofile.branch)  # Filter by the user's branch
    elif user_role == 'MO':  # Maintenance Oversight
        # No additional filtering needed; show all due equipment
        pass
    else:
        # For other roles, return an empty list or restrict access
        due_equipment = Equipment.objects.none()

    context = {
        'due_equipment': due_equipment,
        'active_page':'maintenance_due',
        'notifications':notifications
    }
    return render(request, 'maintenance_due.html', context)

#----------------------------------------------------Import Export-------------------------------------------
def export_data(request, model_name):
    """
    Generalized view for exporting data in Excel format (XLSX).
    """
    # Map model names to their respective resources
    model_resource_map = {
        'Equipment': EquipmentResource,  # Add more models here
        'MaintenanceRecord':MaintenanceRecord,
        # Example: 'Customer': CustomerResource,
    }

    if model_name not in model_resource_map:
        return HttpResponse("Model not supported.", status=400)

    # Get the resource class
    resource_class = model_resource_map[model_name]
    resource = resource_class()

    # Export the data in Excel format (XLSX)
    file_format = base_formats.XLSX()
    dataset = resource.export()
    response = HttpResponse(
        file_format.export_data(dataset),
        content_type=file_format.get_content_type()
    )
    response['Content-Disposition'] = f'attachment; filename={model_name}_export.xlsx'
    return response
#----------------------------------------------------------import--------------------------------------------------

def import_data(request, model_name):
    """
    Generalized view for importing data with a preview page.
    """
    # Map model names to their respective resources
    notifications = get_notifications(request.user)
    model_resource_map = {
        'Equipment': EquipmentResource,  # Add more models here
        # Example: 'Customer': CustomerResource,
    }

    if model_name not in model_resource_map:
        messages.error(request, "Model not supported.")
        return redirect('home')  # Redirect to a safe page

    # Get the resource class
    resource_class = model_resource_map[model_name]
    resource = resource_class()

    if request.method == 'POST':
        if 'confirm_import' in request.POST:
            # Perform the actual import
            import_file = request.FILES['import_file']
            file_format = base_formats.XLSX()  # Only accept Excel files

            # Check if the file is an Excel file
            if not import_file.name.endswith('.xlsx'):
                messages.error(request, "Please upload an Excel file (.xlsx).")
                return redirect('import_data', model_name=model_name)

            # Load the dataset
            dataset = file_format.create_dataset(import_file)
            result = resource.import_data(dataset, dry_run=False)  # Perform the actual import

            if not result.has_errors():
                messages.success(request, 'Data imported successfully.')
            else:
                # Collect errors and display them
                error_messages = []
                for row in result.invalid_rows:
                    error_messages.append(f"Row {row.number}: {row.error}")
                for row in result.row_errors():
                    for error in row[1]:
                        error_messages.append(f"Row {row[0]}: {error.error}")

                # Pass errors to the template
                return render(request, 'import_template.html', {
                    'model_name': model_name,
                    'errors': error_messages,
                })

            return redirect('equipment_list')  # Redirect to the equipment list page

        elif 'import_file' in request.FILES:
            # Perform a dry-run to preview the data
            import_file = request.FILES['import_file']
            file_format = base_formats.XLSX()  # Only accept Excel files

            # Check if the file is an Excel file
            if not import_file.name.endswith('.xlsx'):
                messages.error(request, "Please upload an Excel file (.xlsx).")
                return redirect('import_data', model_name=model_name)

            # Load the dataset
            dataset = file_format.create_dataset(import_file)
            result = resource.import_data(dataset, dry_run=True)  # Perform a dry-run

            # Prepare data for the preview
            preview_data = []
            for row in dataset.dict:
                preview_data.append(row)

            # Collect errors (if any)
            error_messages = []
            for row in result.invalid_rows:
                error_messages.append(f"Row {row.number}: {row.error}")
            for row in result.row_errors():
                for error in row[1]:
                    error_messages.append(f"Row {row[0]}: {error.error}")

            return render(request, 'import_preview.html', {
                'model_name': model_name,
                'preview_data': preview_data,
                'errors': error_messages,
                'active_page':'equipment_list',
                'notifications':notifications,
            })

    return render(request, 'import_template.html', {
        'model_name': model_name,
        'active_page':'equipment_list',
        'notifications':notifications,
    })
    
    
def maintenance_dashboard(request):
    user = request.user
    notifications = get_notifications(request.user)

    user_role = user.userprofile.role
    user_branch = user.userprofile.branch

    # Get date range from request
    from_date = request.GET.get('from_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    to_date = request.GET.get('to_date', datetime.now().strftime('%Y-%m-%d'))

    # Equipment status counts
    operational_count = Equipment.objects.filter(
        branch=user_branch,
        status='operational',
        created_at__range=[from_date, to_date]
    ).count()
    non_operational_count = Equipment.objects.filter(
        branch=user_branch,
        status='non_operational',
        created_at__range=[from_date, to_date]
    ).count()
    under_maintenance_count = Equipment.objects.filter(
        branch=user_branch,
        status='under_maintenance',
        created_at__range=[from_date, to_date]
    ).count()

    # Maintenance by frequency counts
    daily_maintenance_count = MaintenanceRecord.objects.filter(
        branch=user_branch,
        maintenance_type='daily',
        datetime__range=[from_date, to_date]
    ).count()
    weekly_maintenance_count = MaintenanceRecord.objects.filter(
        branch=user_branch,
        maintenance_type='weekly',
        datetime__range=[from_date, to_date]
    ).count()
    monthly_maintenance_count = MaintenanceRecord.objects.filter(
        branch=user_branch,
        maintenance_type='monthly',
        datetime__range=[from_date, to_date]
    ).count()
    biannual_maintenance_count = MaintenanceRecord.objects.filter(
        branch=user_branch,
        maintenance_type='biannual',
        datetime__range=[from_date, to_date]
    ).count()
    annual_maintenance_count = MaintenanceRecord.objects.filter(
        branch=user_branch,
        maintenance_type='annual',
        datetime__range=[from_date, to_date]
    ).count()

    # Work orders counts
    pending_work_orders = WorkOrder.objects.filter(
        branch=user_branch,
        status='Pending',
        created_at__range=[from_date, to_date]
    ).count()
    completed_work_orders = WorkOrder.objects.filter(
        branch=user_branch,
        status='Complete',
        created_at__range=[from_date, to_date]
    ).count()

    # Maintenance by month data
    maintenance_months = []
    maintenance_by_month_data = []
    for i in range(1, 13):  # January to December
        month = datetime(datetime.now().year, i, 1).strftime('%b')
        maintenance_months.append(month)
        maintenance_count = MaintenanceRecord.objects.filter(
            branch=user_branch,
            datetime__month=i,
            datetime__year=datetime.now().year
        ).count()
        maintenance_by_month_data.append(maintenance_count)

    # Work orders by month data
    work_order_months = []
    pending_work_orders_by_month = []
    completed_work_orders_by_month = []
    for i in range(1, 13):  # January to December
        month = datetime(datetime.now().year, i, 1).strftime('%b')
        work_order_months.append(month)
        pending_count = WorkOrder.objects.filter(
            branch=user_branch,
            created_at__month=i,
            created_at__year=datetime.now().year,
            status='Pending'
        ).count()
        completed_count = WorkOrder.objects.filter(
            branch=user_branch,
            created_at__month=i,
            created_at__year=datetime.now().year,
            status='Complete'
        ).count()
        pending_work_orders_by_month.append(pending_count)
        completed_work_orders_by_month.append(completed_count)

    # Spare part usage data
    spare_part_usage = SparePartUsage.objects.filter(
        (Q(maintenance_record__branch=user_branch) | Q(work_order__branch=user_branch)),
        created_at__range=[from_date, to_date]
    ).values('spare_part__name').annotate(total_used=Sum('quantity_used'))

    # Extract labels and data
    spare_part_labels = [item['spare_part__name'] for item in spare_part_usage if item['spare_part__name']]
    spare_part_usage_data = [item['total_used'] for item in spare_part_usage if item['spare_part__name']]

    # Debugging
    print("Spare Part Labels:", spare_part_labels)
    print("Spare Part Usage Data:", spare_part_usage_data)

    # Fallback for empty data
    if not spare_part_labels:
        spare_part_labels = ["No Data"]
        spare_part_usage_data = [0]
    context = {
        'from_date': from_date,
        'to_date': to_date,
        'operational_count': operational_count,
        'non_operational_count': non_operational_count,
        'under_maintenance_count': under_maintenance_count,
        'daily_maintenance_count': daily_maintenance_count,
        'weekly_maintenance_count': weekly_maintenance_count,
        'monthly_maintenance_count': monthly_maintenance_count,
        'biannual_maintenance_count': biannual_maintenance_count,
        'annual_maintenance_count': annual_maintenance_count,
        'pending_work_orders': pending_work_orders,
        'completed_work_orders': completed_work_orders,
        'maintenance_months': maintenance_months,
        'maintenance_by_month_data': maintenance_by_month_data,
        'work_order_months': work_order_months,
        'pending_work_orders_by_month': pending_work_orders_by_month,
        'completed_work_orders_by_month': completed_work_orders_by_month,
        'spare_part_labels': spare_part_labels,
        'spare_part_usage_data': spare_part_usage_data,
        'active_page':'dashboard',
        'notifications':notifications
    }

    return render(request, 'maintenance_dashboard.html', context)

#-----------------------------------------------------------------------------------------

def generate_report(request):
    user = request.user
    user_branch = user.userprofile.branch

    # Get date range and report type from request
    from_date = request.GET.get('from_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    to_date = request.GET.get('to_date', datetime.now().strftime('%Y-%m-%d'))
    report_type = request.GET.get('report_type', 'daily')
    export_format = request.GET.get('format')  # Default to PDF

    if report_type == 'work_order':
        # Fetch work orders with status 'Approved' based on date range
        work_orders = WorkOrder.objects.filter(
            branch=user_branch,
            status='Approved',
            created_at__range=[from_date, to_date]
        ).order_by('created_at')

        if export_format == 'docx':
            return generate_editable_doc_work_order(work_orders, report_type, from_date, to_date)
        else:
            return generate_pdf_work_order(work_orders, report_type, from_date, to_date)
    else:
        # Fetch maintenance records based on report type and date range
        maintenance_records = MaintenanceRecord.objects.filter(
            branch=user_branch,
            maintenance_type=report_type,
            datetime__range=[from_date, to_date]
        ).order_by('datetime')

        if export_format == 'docx':
            return generate_editable_doc(maintenance_records, report_type, from_date, to_date)
        else:
            return generate_pdf(maintenance_records, report_type, from_date, to_date)
        
def generate_pdf(maintenance_records, report_type, from_date, to_date):
    # Create a PDF document
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{report_type}_maintenance_report.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []

    # Add title
    styles = getSampleStyleSheet()
    title = Paragraph(f"{report_type.capitalize()} Maintenance Report", styles['Title'])
    elements.append(title)

    # Add branch and date range
    elements.append(Paragraph(f"Branch: {maintenance_records[0].branch.name}", styles['Normal']))
    elements.append(Paragraph(f"From  {from_date}  to  {to_date}", styles['Normal']))

    space_style = ParagraphStyle(name='Space', spaceAfter=30)  # Adjust spaceAfter value as needed
    elements.append(Paragraph("", space_style))  # Empty paragraph with spacing


    for record in maintenance_records:
        # Add header for each maintenance record
        elements.append(Paragraph(f"Maintenance Date: {record.datetime.strftime('%Y-%m-%d')}, Time: {record.datetime.strftime('%H:%M')}", styles['Heading5']))
        elements.append(Paragraph(f"Equipment: {record.equipment.name} (Serial: {record.equipment.serial_number}), Location: {record.equipment.location}", styles['Normal']))
        space_style = ParagraphStyle(name='Space', spaceAfter=8)  # Adjust spaceAfter value as needed
        elements.append(Paragraph("", space_style))  # Empty paragraph with spacing

        # Create table data
        data = [['No.', 'Inspection', 'Yes', 'No', 'Remarks']]
        task_completions = TaskCompletion.objects.filter(maintenance_record=record)
        for i, task_completion in enumerate(task_completions, start=1):
            task = task_completion.task
            data.append([
                str(i),
                task.description,
                '✓' if task_completion.completed_by else '',
                '✓' if not task_completion.completed_by else '',
                ''  # Empty remarks column for editing
            ])

        # Create table
        table = Table(data, colWidths=[0.3*inch, 4*inch, 0.3*inch, 0.3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        elements.append(table)
        space_style = ParagraphStyle(name='Space', spaceAfter=8)  # Adjust spaceAfter value as needed
        elements.append(Paragraph("", space_style))  # Empty paragraph with spacing

        # Add inspected by and approved by sections
        inspected_by = [tech.get_full_name() for tech in record.assigned_technicians.all()]
        approved_by = record.approved_by.get_full_name() if record.approved_by else "N/A"

        # Create a table with one row and two columns
        table_data = [
            [
                Paragraph(f"<b>Inspected by:</b><br/><br/>" + "<br/><br/>".join(inspected_by)),  # Left column
                Paragraph(f"<b>Approved by:</b><br/><br/>{approved_by}")  # Right column
            ]
        ]

        # Define column widths (adjust as needed)
        col_widths = [3 * inch, 3 * inch]  # Equal width for both columns

        # Create the table
        table = Table(table_data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # Align text to the left
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Align text to the top
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),  # Add padding at the bottom
        ]))

        # Add the table to the elements
        elements.append(table)
                # Add space between records
        elements.append(Paragraph("<br/><br/>", styles['Normal']))

    # Build the PDF
    doc.build(elements)
    return response

#-----------------------------------------------------------------------------------------

def generate_editable_doc(maintenance_records, report_type, from_date, to_date):
    # Create a Word document
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = f'attachment; filename="{report_type}_maintenance_report.docx"'

    doc = Document()

    # Add main title
    title = doc.add_heading(f"{report_type.capitalize()} Maintenance Report", level=1)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER 
    title.style.font.size = Pt(18)  # Make the title smaller

    # Add branch and date range
    branch_paragraph = doc.add_paragraph(f"Branch: {maintenance_records[0].branch.name}", style='Intense Quote' )
    branch_paragraph.paragraph_format.space_after = Pt(0)
    date_paragraph = doc.add_paragraph(f"From {from_date} to {to_date}", style='Intense Quote')
    date_paragraph.paragraph_format.space_before = Pt(0)  # Remove space before this paragraph
    date_paragraph.paragraph_format.space_after = Pt(20)  # add space before this paragraph


    for record in maintenance_records:
        # Add header for each maintenance record
        doc.add_heading(f"Maintenance Date: {record.datetime.strftime('%Y-%m-%d')}, Time: {record.datetime.strftime('%H:%M')}", level=3)
        doc.add_paragraph(f"Equipment: {record.equipment.name} (Serial: {record.equipment.serial_number}), Location: {record.equipment.location}")

        # Create table
        table = doc.add_table(rows=1, cols=5)
        table.style = 'Table Grid'
        table.autofit = False

        # Set column widths
        col_widths = [0.2, 4, 0.2, 0.2, 2]  # Widths in inches
        for i, width in enumerate(col_widths):
            col = table.columns[i]
            col.width = Inches(width)

        # Add table headers
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = 'No.'
        hdr_cells[1].text = 'Inspection'
        hdr_cells[2].text = 'Yes'
        hdr_cells[3].text = 'No'
        hdr_cells[4].text = 'Remarks'

        # Access tasks through TaskCompletion
        task_completions = TaskCompletion.objects.filter(maintenance_record=record)
        for i, task_completion in enumerate(task_completions, start=1):
            task = task_completion.task
            row_cells = table.add_row().cells
            row_cells[0].text = str(i)
            row_cells[1].text = task.description
            row_cells[2].text = '✓' if task_completion.completed_by else ''
            row_cells[3].text = '✓' if not task_completion.completed_by else ''
            row_cells[4].text = ''  # Empty remarks column for editing

        space_paragraph = doc.add_paragraph()
        space_paragraph.paragraph_format.space_after = Pt(0.1)  # Adjust the space as needed
        # Add inspected by and approved by sections
        inspected_by = [tech.get_full_name() for tech in record.assigned_technicians.all()]
        approved_by = record.approved_by.get_full_name() if record.approved_by else "N/A"

        # Create a table with one row and two columns
        table = doc.add_table(rows=1, cols=2)
        table.autofit = False

        # Set column widths (adjust as needed)
        table.columns[0].width = Inches(3)  # Width for the "Inspected by" column
        table.columns[1].width = Inches(3)  # Width for the "Approved by" column

        # Add "Inspected by" to the first cell
        inspected_by_cell = table.rows[0].cells[0]
        inspected_by_cell.text = "Inspected by:"
        for paragraph in inspected_by_cell.paragraphs:
            for run in paragraph.runs:
                run.bold = True  # Make "Inspected by" bold

        # Add technician names below "Inspected by"
        for tech in inspected_by:
            inspected_by_cell.add_paragraph(tech, style='List Bullet')

        # Add "Approved by" to the second cell
        approved_by_cell = table.rows[0].cells[1]
        approved_by_paragraph = approved_by_cell.add_paragraph()
        approved_by_paragraph.add_run("Approved by: ").bold = True  # Make "Approved by" bold
        approved_by_paragraph.add_run(approved_by)

        # Add space between records
        doc.add_paragraph()
    # Save the document to a BytesIO stream
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    response.write(buffer.getvalue())
    buffer.close()

    return response
#----------------------------------------------------------------------------------------------------

def generate_pdf_work_order(work_orders, report_type, from_date, to_date):
    # Create a PDF document
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{report_type}_work_order_report.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []

    # Add title
    styles = getSampleStyleSheet()
    title = Paragraph(f"Work Order Report", styles['Title'])
    elements.append(title)

    # Add branch and date range
    elements.append(Paragraph(f"Branch: {work_orders[0].branch.name}", styles['Normal']))
    elements.append(Paragraph(f"From  {from_date}  to  {to_date}", styles['Normal']))

    space_style = ParagraphStyle(name='Space', spaceAfter=30)  # Adjust spaceAfter value as needed
    elements.append(Paragraph("", space_style))  # Empty paragraph with spacing

    # Create table data
    data = [['Equipment', 'Location', 'Requester']]
    for work_order in work_orders:
        data.append([
            work_order.equipment.name,
            work_order.equipment.location,
            work_order.requester.get_full_name()
        ])

    # Create table
    table = Table(data, colWidths=[3*inch, 3*inch, 2*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(table)

    # Add Technician and Approved By sections
    for work_order in work_orders:
        # Add space between records
        elements.append(Paragraph("<br/><br/>", styles['Normal']))

        # Create a table with one row and two columns
        table_data = [
            [
                Paragraph(f"<b>Technician:</b><br/><br/>" + "<br/><br/>".join([tech.get_full_name() for tech in work_order.assigned_technicians.all()])),  # Left column
                Paragraph(f"<b>Approved By:</b><br/><br/>{work_order.approved_by.get_full_name() if work_order.approved_by else 'N/A'}")  # Right column
            ]
        ]

        # Define column widths (adjust as needed)
        col_widths = [3 * inch, 3 * inch]  # Equal width for both columns

        # Create the table
        table = Table(table_data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # Align text to the left
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Align text to the top
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),  # Add padding at the bottom
        ]))

        # Add the table to the elements
        elements.append(table)

    # Build the PDF
    doc.build(elements)
    return response
#------------------------------------------------------------------------------------------------------
def generate_editable_doc_work_order(work_orders, report_type, from_date, to_date):
    # Create a Word document
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = f'attachment; filename="{report_type}_work_order_report.docx"'

    doc = Document()

    # Add main title
    title = doc.add_heading("Work Order Report", level=1)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.style.font.size = Pt(18)  # Make the title smaller

    # Add branch and date range
    branch_paragraph = doc.add_paragraph(f"Branch: {work_orders[0].branch.name}", style='Intense Quote')
    branch_paragraph.paragraph_format.space_after = Pt(0)
    date_paragraph = doc.add_paragraph(f"From {from_date} to {to_date}", style='Intense Quote')
    date_paragraph.paragraph_format.space_before = Pt(0)  # Remove space before this paragraph
    date_paragraph.paragraph_format.space_after = Pt(20)  # Add space after this paragraph

    # Create table
    table = doc.add_table(rows=1, cols=3)
    table.style = 'Table Grid'
    table.autofit = False

    # Set column widths
    col_widths = [3, 3, 2]  # Widths in inches
    for i, width in enumerate(col_widths):
        col = table.columns[i]
        col.width = Inches(width)

    # Add table headers
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Equipment'
    hdr_cells[1].text = 'Location'
    hdr_cells[2].text = 'Requester'

    # Add work order data
    for work_order in work_orders:
        row_cells = table.add_row().cells
        row_cells[0].text = work_order.equipment.name
        row_cells[1].text = work_order.equipment.location
        row_cells[2].text = work_order.requester.get_full_name()

        # Add space between records
        doc.add_paragraph()

        # Create a table with one row and two columns
        table = doc.add_table(rows=1, cols=2)
        table.autofit = False

        # Set column widths (adjust as needed)
        table.columns[0].width = Inches(3)  # Width for the "Technician" column
        table.columns[1].width = Inches(3)  # Width for the "Approved by" column

        # Add "Technician" to the first cell
        technician_cell = table.rows[0].cells[0]
        technician_cell.text = "Technician:"
        for paragraph in technician_cell.paragraphs:
            for run in paragraph.runs:
                run.bold = True  # Make "Technician" bold

        # Add technician names below "Technician"
        for tech in work_order.assigned_technicians.all():
            technician_cell.add_paragraph(tech.get_full_name(), style='List Bullet')

        # Add "Approved by" to the second cell
        approved_by_cell = table.rows[0].cells[1]
        approved_by_paragraph = approved_by_cell.add_paragraph()
        approved_by_paragraph.add_run("Approved by: ").bold = True  # Make "Approved by" bold
        approved_by_paragraph.add_run(work_order.approved_by.get_full_name() if work_order.approved_by else "N/A")

    # Save the document to a BytesIO stream
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    response.write(buffer.getvalue())
    buffer.close()

    return response

#--------------------------------------------------------------------------------------------------------



def maintenance_oversight_dashboard(request):
    user = request.user
    notifications = get_notifications(request.user)

    user_role = user.userprofile.role

    # Get date range from request
    from_date = request.GET.get('from_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    to_date = request.GET.get('to_date', datetime.now().strftime('%Y-%m-%d'))

    # Get selected branch from request
    selected_branch = request.GET.get('branch', 'all')

    # Filter by branch if a specific branch is selected
    if selected_branch == 'all':
        branch_filter = {}
    else:
        branch_filter = {'branch': selected_branch}

    # Equipment status counts
    operational_count = Equipment.objects.filter(
        **branch_filter,
        status='operational',
        created_at__range=[from_date, to_date]
    ).count()
    non_operational_count = Equipment.objects.filter(
        **branch_filter,
        status='non_operational',
        created_at__range=[from_date, to_date]
    ).count()
    under_maintenance_count = Equipment.objects.filter(
        **branch_filter,
        status='under_maintenance',
        created_at__range=[from_date, to_date]
    ).count()

    # Maintenance by frequency counts
    daily_maintenance_count = MaintenanceRecord.objects.filter(
        **branch_filter,
        maintenance_type='daily',
        datetime__range=[from_date, to_date]
    ).count()
    weekly_maintenance_count = MaintenanceRecord.objects.filter(
        **branch_filter,
        maintenance_type='weekly',
        datetime__range=[from_date, to_date]
    ).count()
    monthly_maintenance_count = MaintenanceRecord.objects.filter(
        **branch_filter,
        maintenance_type='monthly',
        datetime__range=[from_date, to_date]
    ).count()
    biannual_maintenance_count = MaintenanceRecord.objects.filter(
        **branch_filter,
        maintenance_type='biannual',
        datetime__range=[from_date, to_date]
    ).count()
    annual_maintenance_count = MaintenanceRecord.objects.filter(
        **branch_filter,
        maintenance_type='annual',
        datetime__range=[from_date, to_date]
    ).count()

    # Work orders counts
    pending_work_orders = WorkOrder.objects.filter(
        **branch_filter,
        status='Pending',
        created_at__range=[from_date, to_date]
    ).count()
    completed_work_orders = WorkOrder.objects.filter(
        **branch_filter,
        status='Complete',
        created_at__range=[from_date, to_date]
    ).count()

    # Maintenance by month data
    maintenance_months = []
    maintenance_by_month_data = []
    for i in range(1, 13):  # January to December
        month = datetime(datetime.now().year, i, 1).strftime('%b')
        maintenance_months.append(month)
        maintenance_count = MaintenanceRecord.objects.filter(
            **branch_filter,
            datetime__month=i,
            datetime__year=datetime.now().year
        ).count()
        maintenance_by_month_data.append(maintenance_count)

    # Work orders by month data
    work_order_months = []
    pending_work_orders_by_month = []
    completed_work_orders_by_month = []
    for i in range(1, 13):  # January to December
        month = datetime(datetime.now().year, i, 1).strftime('%b')
        work_order_months.append(month)
        pending_count = WorkOrder.objects.filter(
            **branch_filter,
            created_at__month=i,
            created_at__year=datetime.now().year,
            status='Pending'
        ).count()
        completed_count = WorkOrder.objects.filter(
            **branch_filter,
            created_at__month=i,
            created_at__year=datetime.now().year,
            status='Complete'
        ).count()
        pending_work_orders_by_month.append(pending_count)
        completed_work_orders_by_month.append(completed_count)

    # Spare part usage data
    spare_part_usage = SparePartUsage.objects.filter(
        (Q(maintenance_record__branch=selected_branch) | Q(work_order__branch=selected_branch)) if selected_branch != 'all' else Q(),
        created_at__range=[from_date, to_date]
    ).values('spare_part__name').annotate(total_used=Sum('quantity_used'))

    # Extract labels and data
    spare_part_labels = [item['spare_part__name'] for item in spare_part_usage if item['spare_part__name']]
    spare_part_usage_data = [item['total_used'] for item in spare_part_usage if item['spare_part__name']]

    # Debugging
    print("Spare Part Labels:", spare_part_labels)
    print("Spare Part Usage Data:", spare_part_usage_data)

    # Fallback for empty data
    if not spare_part_labels:
        spare_part_labels = ["No Data"]
        spare_part_usage_data = [0]

    # Get all branches for the dropdown
    all_branches = Branch.objects.all()

    context = {
        'from_date': from_date,
        'to_date': to_date,
        'selected_branch': selected_branch,
        'all_branches': all_branches,
        'operational_count': operational_count,
        'non_operational_count': non_operational_count,
        'under_maintenance_count': under_maintenance_count,
        'daily_maintenance_count': daily_maintenance_count,
        'weekly_maintenance_count': weekly_maintenance_count,
        'monthly_maintenance_count': monthly_maintenance_count,
        'biannual_maintenance_count': biannual_maintenance_count,
        'annual_maintenance_count': annual_maintenance_count,
        'pending_work_orders': pending_work_orders,
        'completed_work_orders': completed_work_orders,
        'maintenance_months': maintenance_months,
        'maintenance_by_month_data': maintenance_by_month_data,
        'work_order_months': work_order_months,
        'pending_work_orders_by_month': pending_work_orders_by_month,
        'completed_work_orders_by_month': completed_work_orders_by_month,
        'spare_part_labels': spare_part_labels,
        'spare_part_usage_data': spare_part_usage_data,
        'active_page': 'dashboard',
        'notifications': notifications
    }

    return render(request, 'maintenance_oversight_dashboard.html', context)
def export_maintenance_report_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="maintenance_report.pdf"'

    # Create a PDF document
    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []

    # Add a title
    styles = getSampleStyleSheet()
    title = Paragraph("Maintenance Report", styles['Title'])
    elements.append(title)

    # Prepare data for the table
    maintenance_records = MaintenanceRecord.objects.all()
    data = [['Equipment', 'Maintenance Task', 'Status', 'Date', 'Tasks Completed']]
    for record in maintenance_records:
        tasks_completed = ', '.join([task.description for task in record.completed_tasks.all()])
        data.append([
            record.equipment.name,
            record.maintenance_task.equipment_type,
            record.status,
            record.datetime.strftime('%Y-%m-%d'),
            tasks_completed
        ])

    # Create a table
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(table)

    # Build the PDF
    doc.build(elements)
    return response


def dashboard(request):
    # Check if the user is an admin (AD)
    if request.user.userprofile.role != 'AD':
        return HttpResponse("You do not have permission to access this page.")

    notifications = get_notifications(request.user)

    user_count = User.objects.count()
    equipment_count = Equipment.objects.count()
    branch_count = User.objects.values('userprofile__branch').distinct().count()

    context = {
        'user_count': user_count,
        'equipment_count': equipment_count,
        'branch_count': branch_count,
        'notifications': notifications,
        'active_page': 'dashboard'
    }

    return render(request, 'dashboard.html', context)