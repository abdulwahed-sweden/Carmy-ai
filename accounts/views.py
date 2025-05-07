# accounts/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import UserProfile, UserVehicle, DiagnosticHistory, MaintenanceRecord
from .serializers import (UserSerializer, UserProfileSerializer, 
                         UserVehicleSerializer, DiagnosticHistorySerializer,
                         MaintenanceRecordSerializer)

class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

class UserVehicleViewSet(viewsets.ModelViewSet):
    serializer_class = UserVehicleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserVehicle.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        # If this is set as primary, unset others
        if serializer.validated_data.get('is_primary', False):
            UserVehicle.objects.filter(
                user=self.request.user, 
                is_primary=True
            ).update(is_primary=False)
        serializer.save(user=self.request.user)

class DiagnosticHistoryViewSet(viewsets.ModelViewSet):
    serializer_class = DiagnosticHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return DiagnosticHistory.objects.filter(
            vehicle__user=self.request.user
        ).order_by('-date')
    
    @action(detail=False, methods=['get'])
    def vehicle(self, request):
        vehicle_id = request.query_params.get('vehicle_id')
        if not vehicle_id:
            return Response(
                {'error': 'Vehicle ID is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(vehicle_id=vehicle_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class MaintenanceRecordViewSet(viewsets.ModelViewSet):
    serializer_class = MaintenanceRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return MaintenanceRecord.objects.filter(
            vehicle__user=self.request.user
        ).order_by('-date')