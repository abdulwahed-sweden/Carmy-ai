# accounts/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, UserVehicle, DiagnosticHistory, MaintenanceRecord
from car_diagnostics.serializers import CarListSerializer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = '__all__'

class UserVehicleSerializer(serializers.ModelSerializer):
    car_details = CarListSerializer(source='car', read_only=True)
    
    class Meta:
        model = UserVehicle
        fields = ['id', 'car', 'car_details', 'nickname', 'purchase_date', 
                 'license_plate', 'is_primary']

class DiagnosticHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DiagnosticHistory
        fields = '__all__'

class MaintenanceRecordSerializer(serializers.ModelSerializer):
    maintenance_type_display = serializers.CharField(source='get_maintenance_type_display', read_only=True)
    
    class Meta:
        model = MaintenanceRecord
        fields = ['id', 'vehicle', 'maintenance_type', 'maintenance_type_display',
                 'date', 'mileage', 'service_provider', 'cost', 'description']