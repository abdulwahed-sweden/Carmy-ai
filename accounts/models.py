# accounts/models.py
from django.db import models
from django.contrib.auth.models import User
from car_diagnostics.models import Car

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    preferred_language = models.CharField(
        max_length=10, 
        choices=[('en', 'English'), ('ar', 'Arabic')],
        default='en'
    )
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

class UserVehicle(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vehicles')
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=50, blank=True, null=True)
    purchase_date = models.DateField(blank=True, null=True)
    license_plate = models.CharField(max_length=20, blank=True, null=True)
    is_primary = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username}'s {self.car} ({self.nickname})"
    

# accounts/models.py (continued)
class DiagnosticHistory(models.Model):
    vehicle = models.ForeignKey(UserVehicle, on_delete=models.CASCADE, related_name='diagnostics')
    date = models.DateTimeField(auto_now_add=True)
    obd_codes = models.JSONField()
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Diagnostic for {self.vehicle} on {self.date.strftime('%Y-%m-%d')}"

class MaintenanceRecord(models.Model):
    MAINTENANCE_TYPES = [
        ('oil_change', 'Oil Change'),
        ('tire_rotation', 'Tire Rotation'),
        ('brake_service', 'Brake Service'),
        ('engine_repair', 'Engine Repair'),
        ('scheduled', 'Scheduled Maintenance'),
        ('other', 'Other')
    ]
    
    vehicle = models.ForeignKey(UserVehicle, on_delete=models.CASCADE, related_name='maintenance')
    maintenance_type = models.CharField(max_length=20, choices=MAINTENANCE_TYPES)
    date = models.DateField()
    mileage = models.IntegerField()
    service_provider = models.CharField(max_length=100, blank=True, null=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.get_maintenance_type_display()} for {self.vehicle} on {self.date}"