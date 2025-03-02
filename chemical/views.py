from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Chemical , RestockChemical, ChemicalUsage
from .forms import ChemicalForm, RestockChemicalForm
from maintenance.models import Branch
from django.contrib.auth.models import User
from django.utils import timezone
from maintenance.forms import BranchForm


# Create your views here.


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
    Log = ChemicalUsage.objects.filter(chemical = chemical).order_by('-date_used')
    if request.method == 'POST':
        form = ChemicalForm(request.POST, instance=chemical)
        if form.is_valid():
            form.save()  # Save the changes to the database
            messages.success(request, 'Chemical updated successfully!')
            return redirect('chemical_list')  # Redirect to the chemical list
    else:
        form = ChemicalForm(instance=chemical)  # Pre-fill the form with the current data

    return render(request, 'edit_chemical.html', {'form': form, 'chemical': chemical, 'active_page': 'chemical_list','notifications':notifications, 'Log':Log
})
    

def chemical_usage(request):
    chemicals = Chemical.objects.all()  # Filter chemicals by user's branch
    context = {
        'chemicals': chemicals,
        'active_page': 'chemical_usage',
        'branch': request.user.userprofile.branch,  # Default branch based on the user
    }

    if request.method == 'POST':
        chemical_id = request.POST.get('chemical')
        quantity = float(request.POST.get('quantity'))
        purpose = request.POST.get('purpose')

        try:
            chemical = Chemical.objects.get(id=chemical_id)

            # Check if there's enough quantity
            if chemical.quantity_available >= quantity:
                # Decrease the quantity
                chemical.quantity_available -= quantity
                chemical.save()

                # Log the usage in the Chemical model (optional)
                if chemical.usage_log:
                    chemical.usage_log += f"\n{request.user.get_full_name()} used {quantity} {chemical.unit_of_measurement} for {purpose} on {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}."
                else:
                    chemical.usage_log = f"{request.user.get_full_name()} used {quantity} {chemical.unit_of_measurement} for {purpose} on {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}."
                chemical.save()

                # Create a ChemicalUsage record
                ChemicalUsage.objects.create(
                    chemical=chemical,
                    quantity_used=quantity,
                    user=request.user,
                    branch=request.user.userprofile.branch,
                    purpose=purpose,
                    date_used=timezone.now()
                )

                messages.success(request, f"{quantity} {chemical.unit_of_measurement} of {chemical.chemical_name} used.")
            else:
                messages.error(request, f"Insufficient quantity available for {chemical.chemical_name}.")

        except Chemical.DoesNotExist:
            messages.error(request, "Invalid chemical selected.")

        return redirect('chemical_usage')

    return render(request, 'chemical_usage.html', context)

def chemical_usage_list(request):
    usage_list = ChemicalUsage.objects.all().order_by('-date_used')
    
    context = {
        'usage_list': usage_list,
        'active_page': 'chemical_usage_list',
    }
    
    return render(request, 'chemical_usage_list.html', context)

def restock_chemical(request):
    notifications = get_notifications(request.user)

    if request.method == 'POST':
        selected_chemical_id = request.POST.get('chemical')  # Get the selected chemical ID
        chemical = get_object_or_404(Chemical, id=selected_chemical_id)  # Fetch the chemical instance

        form = RestockChemicalForm(request.POST, request.FILES)
        if form.is_valid(): 
            restock = form.save(commit=False)
            restock.chemical = chemical  # Associate the restock with the chemical
            restock.restock_date = timezone.now()  # Set the restock date to the current time
            restock.save()

            # Update the chemical quantity and last_restock_date
            chemical.quantity_available += restock.quantity  # Assuming quantity is a field in Chemical
            chemical.last_restock_date = restock.restock_date  # Assuming this field exists
            chemical.save()

            messages.success(request, f'{restock.quantity} units of {chemical.chemical_name} restocked successfully!')
            return redirect('chemical_list')  # Redirect to the appropriate page
    else:
        form = RestockChemicalForm()

    # Pass a list of chemicals to the template
    # user_branch = request.user.userprofile.branch
    chemicals = Chemical.objects.all()

    context = {
        'form': form,
        'chemicals': chemicals,  # Ensure you pass all chemicals to the template
        'active_page': 'chemical_list',
        'notifications': notifications,
    }
    return render(request, 'restock_chemical.html', context)

def chemical_restock_list(request):
    # Get the user's branch
    

    # Fetch restock records for chemicals in the user's branch
    restock_list = RestockChemical.objects.all().order_by('-restock_date')

    # Get notifications for the user
    notifications = get_notifications(request.user)

    context = {
        'restock_list': restock_list,
        'active_page': 'chemical_restock_list',
        'notifications': notifications,
        'title': 'Chemical Restock List',
    }

    return render(request, 'chemical_restock_list.html', context)

def expiring_chemical(request):
    # Fetch users with the role 'CO'
    users = User.objects.filter(userprofile__role='CO')

    # Get today's date
    today = timezone.now().date()

    # Calculate the threshold date (10 days from today)
    threshold_date = today + timezone.timedelta(days=10)

    # Fetch chemicals that are expiring in 10 days or less
    expiring_chemicals = Chemical.objects.filter(expiration_date__lte=threshold_date)

    # Calculate days until expiration for each chemical
    for chemical in expiring_chemicals:
        if chemical.expiration_date:
            delta = (chemical.expiration_date - today).days
            chemical.days_until_expiration = delta
        else:
            chemical.days_until_expiration = None

    # Get notifications for the user
    notifications = get_notifications(request.user)

    # Create notifications for expiring chemicals
    for chemical in expiring_chemicals:
        expiration_date_formatted = chemical.expiration_date.strftime('%Y-%m-%d')
        notification_message = f"{chemical.chemical_name} is expiring on {expiration_date_formatted}."
        for user in users:
            Notification.objects.create(user=user,type ='expiration_list', message=notification_message)

    context = {
        'expiring_chemicals': expiring_chemicals,
        'active_page': 'expiring_chemical',
        'notifications': notifications,
        'title': 'Expiring Chemicals',
    }

    return render(request, 'expired_chemical.html', context)