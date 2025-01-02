from django.db import models
from django.conf import settings
import uuid

# Lab model with choices
class Lab(models.Model):
    # Predefined choices for labs
    LAB_CHOICES = [
        ('LAB1', 'Lab 1'),
        ('LAB2', 'Lab 2'),
        ('LAB3', 'Lab 3'),
    ]
    name = models.CharField(max_length=100, choices=LAB_CHOICES, unique=True, default='LAB1')

    def __str__(self):
        return self.name


# Cabinet model with choices
class Cabinet(models.Model):
    # Predefined choices for cabinets
    lab = models.ForeignKey(Lab, related_name='cabinets', on_delete=models.CASCADE)
    cabinet_number = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('lab', 'cabinet_number')

    def __str__(self):
        return f"Cabinet {self.cabinet_number} in {self.lab.name}"


# Shelve model with choices
class Shelf(models.Model):
    # Predefined choices for shelf
    cabinet = models.ForeignKey(Cabinet, related_name='shelves', on_delete=models.CASCADE)
    shelf_number = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cabinet', 'shelf_number')

    def __str__(self):
        return f"shelf {self.shelf_number} in {self.cabinet}"



class Chemical(models.Model):
    """
    Represents a chemical entity.
    """
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    name = models.CharField(max_length=100)
    quantity = models.FloatField(help_text="in gram(g) or liter(L)")
    description = models.TextField()
    vendor = models.CharField(max_length=100)
    hazard_information = models.TextField()
    molecular_formula = models.CharField(max_length=100)
    reactivity_group = models.CharField(max_length=255, choices=[
        ('Alkali', 'Alkali'),
        ('Alkaline Earth', 'Alkaline Earth'),
        ('Transition Metal', 'Transition Metal'),
        ('Lanthanide', 'Lanthanide'),
        ('Actinide', 'Actinide'),
        ('Metal', 'Metal'),
        ('Nonmetal', 'Nonmetal'),
        ('Halogen', 'Halogen'),
        ('Noble Gas', 'Noble Gas'),
        ('Other', 'Other'),
    ])
    chemical_type = models.CharField(max_length=100, choices=[
        ('Organic', 'Organic'),
        ('Inorganic', 'Inorganic'),
        ('Both', 'Both'),
    ])
    chemical_state = models.CharField(max_length=100, choices=[
        ('Solid', 'Solid'),
        ('Liquid', 'Liquid'),
        ('Gas', 'Gas'),
        ('Plasma', 'Plasma'),
        ('Other', 'Other'),
    ])
    Shelf = models.ForeignKey(Shelf, on_delete=models.CASCADE, related_name='chemicals')
    expires = models.DateField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_chemical')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
