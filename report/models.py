from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

# Create your models here.
class Report(models.Model):
    REPORT_TYPE_CHOICES = [
        ('inventory','Inventory Report'),
        ('expiry','Expiry Report',),
    ]

    title = models.CharField(max_length=100) # Repport Title
    report_type = models.CharField(max_length=100, choices=REPORT_TYPE_CHOICES, default='inventory')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Use this to reference the user model
        on_delete=models.CASCADE
    ) # Superuser / Lab Attendant who ever generate the report
    generated_on = models.DateField(auto_now_add=True) # Timestamp of Generaion
    file_path = models.FileField(upload_to='reports/', blank=True, null=True)
    filters_applied = models.JSONField(blank=True, null=True)
    is_exported = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.title} - ({self.report_type})'
    
    class Meta:
        ordering = ['-generated_on']
        verbose_name = 'Report'
        verbose_name_plural = 'Reports'