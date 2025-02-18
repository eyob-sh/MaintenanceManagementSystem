from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http import Http404
from datetime import datetime
from .forms.EquipmentForm import EquipmentForm

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
        # 'edit_url': 'edit_spare_part',  # Assuming you have an edit view set up
    }
    return render(request, 'spare_part_list.html', context)

def add_spare_part_page(request):
    branches = Branch.objects.all()
    return render (request, 'add_spare_part.html', {
                'branches': branches,
            })

def add_spare_part(request):
    return render(request, 'dashboard.html')

def edit_spare_part(request, id):
        return render(request, 'spare_part_list')






@login_required()
def dashboard(request):
    return render(request, 'dashboard.html')

@login_required()
def equipment(request):
    return render(request, 'equipment.html')