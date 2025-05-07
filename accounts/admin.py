from django.contrib import admin
from .models import UserProfile, UserVehicle, DiagnosticHistory, MaintenanceRecord

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'preferred_language')
    search_fields = ('user__username', 'user__email', 'phone_number')

@admin.register(UserVehicle)
class UserVehicleAdmin(admin.ModelAdmin):
    list_display = ('user', 'car', 'nickname', 'license_plate', 'is_primary')
    list_filter = ('is_primary',)
    search_fields = ('user__username', 'car__brand', 'car__model', 'license_plate')

@admin.register(DiagnosticHistory)
class DiagnosticHistoryAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'date')
    list_filter = ('date',)
    search_fields = ('vehicle__user__username', 'vehicle__car__brand', 'vehicle__car__model')

@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'maintenance_type', 'date', 'mileage', 'cost')
    list_filter = ('maintenance_type', 'date')
    search_fields = ('vehicle__user__username', 'vehicle__car__brand', 'service_provider')