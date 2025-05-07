# accounts/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (UserProfileViewSet, UserVehicleViewSet, 
                   DiagnosticHistoryViewSet, MaintenanceRecordViewSet)

router = DefaultRouter()
router.register(r'profile', UserProfileViewSet, basename='profile')
router.register(r'vehicles', UserVehicleViewSet, basename='vehicles')
router.register(r'diagnostics', DiagnosticHistoryViewSet, basename='diagnostics')
router.register(r'maintenance', MaintenanceRecordViewSet, basename='maintenance')

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/', include('rest_framework.urls')),
]