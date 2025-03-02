from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from maintenance.models import Branch,UserProfile
from django.utils import timezone
# Create your models here.


class Chemical(models.Model):
    
    UNIT_CHOICES = [
        ('L', 'Liter (L)'),
        ('mL', 'Milliliter (mL)'),
        ('kg', 'Kilogram (kg)'),
        ('g', 'Gram (g)'),
        ('mg', 'Milligram (mg)'),
        ('mol', 'Mole (mol)'),
        ('mmol', 'Millimole (mmol)'),
        ('m³', 'Cubic Meter (m³)'),
        ('cm³', 'Cubic Centimeter (cm³)'),
        ('gal', 'Gallon (gal)'),
        ('lb', 'Pound (lb)'),
        ('oz', 'Ounce (oz)'),
        ('piece', 'Piece'),
        ('unit', 'Unit'),
        ('box', 'Box'),
        ('bottle', 'Bottle'),
        ('pack', 'Pack'),
        ('bag', 'Bag'),
        ('can', 'Can'),
        ('tube', 'Tube'),
        ('carton', 'Carton'),
        ('pallet', 'Pallet'),
    ]
    
    # Chemical Information
    chemical_name = models.CharField(
        max_length=255,
        help_text="Enter the IUPAC or common name of the chemical.",
    )
    cas_number = models.CharField(
        max_length=50,
        unique=True,
        help_text="Enter the Chemical Abstracts Service (CAS) registry number.",
    )
    molecular_formula = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Enter the molecular formula of the chemical (if applicable).",
    )

    # Manufacturer/Supplier Information
    manufacturer_supplier = models.CharField(
        max_length=255,
        help_text="Enter the manufacturer or supplier name (brand/vendor).",
    )
    catalog_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Enter the catalog number (if sourced externally).",
    )
    batch_lot_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Enter the batch or lot number for tracking specific batches.",
    )

    # Quantity and Storage
    quantity_available = models.FloatField(
        validators=[MinValueValidator(0)],
        help_text="Enter the quantity available in stock (e.g., mL, L, g, kg).",
    )
    unit_of_measurement = models.CharField(
        max_length=50,
        choices=UNIT_CHOICES,
        help_text="Select the unit of measurement"
    )
    location_storage_area = models.CharField(
        max_length=255,
        help_text="Enter the location or storage area (e.g., Shelf A, Lab 2, Flammable Cabinet).",
    )
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)

    # Dates
    date_of_entry = models.DateField(
        default=timezone.now,
        help_text="Enter the date when the chemical was added to inventory.",
    )
    expiration_date = models.DateField(
        blank=True,
        null=True,
        help_text="Enter the expiration date to track usability.",
    )

    # Reorder and Safety
    reorder_level = models.FloatField(
        validators=[MinValueValidator(0)],
        help_text="Enter the reorder level threshold to notify restocking needs.",
    )
    sds_link = models.URLField(
        blank=True,
        null=True,
        help_text="Enter the Safety Data Sheet (SDS) link for safety reference.",
    )
    hazard_classification = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Enter the hazard classification (e.g., GHS labeling, NFPA).",
    )

    # Usage Log (Optional, can be handled separately)
    usage_log = models.TextField(
        blank=True,
        null=True,
        help_text="Enter the history of usage and users handling the chemical.",
    )

    def __str__(self):
        return f"{self.chemical_name} ({self.cas_number})"

    class Meta:
        verbose_name = "Chemical"
        verbose_name_plural = "Chemicals"
        ordering = ['chemical_name']


class RestockChemical(models.Model):
    chemical = models.ForeignKey(Chemical, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=0)
    restock_date = models.DateTimeField(auto_now_add=True)
    attachment = models.FileField(upload_to='restock_attachments/', null=True, blank=True)  # Optional attachment

    def __str__(self):
        return f"Restock {self.quantity} units of {self.chemical.name} on {self.restock_date}"


class ChemicalUsage(models.Model):
    chemical = models.ForeignKey(Chemical, on_delete=models.CASCADE, related_name='usage_records')
    quantity_used = models.FloatField(validators=[MinValueValidator(0.01)])
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chemical_usage')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='chemical_usage')
    purpose = models.TextField()
    date_used = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.chemical.chemical_name} - {self.quantity_used} {self.chemical.unit_of_measurement} by {self.user.get_full_name()} on {self.date_used.strftime('%Y-%m-%d')}"
    
