from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CarBrandViewSet, CarViewSet, ErrorCodeCategoryViewSet, ErrorCodeViewSet,
    DiagnosticSearchViewSet, SmartDiagnosticAPIView, OBDSimulatorAPIView,
    OBDDeviceDataAPIView, index, car_search, error_search, smart_diagnostic, obd_scanner
)

app_name = 'car_diagnostics'

# API routes
router = DefaultRouter()
router.register(r'brands', CarBrandViewSet)
router.register(r'cars', CarViewSet)
router.register(r'error-categories', ErrorCodeCategoryViewSet)
router.register(r'error-codes', ErrorCodeViewSet)
router.register(r'diagnostic-search', DiagnosticSearchViewSet, basename='diagnostic-search')

urlpatterns = [
    # Frontend routes
    path('', index, name='index'),
    path('car-search/', car_search, name='car_search'),
    path('error-search/', error_search, name='error_search'),
    path('smart-diagnostic/', smart_diagnostic, name='smart_diagnostic'),
    path('obd-scanner/', obd_scanner, name='obd_scanner'),
    
    # API routes
    path('api/', include(router.urls)),
    path('api/smart-diagnostic/', SmartDiagnosticAPIView.as_view(), name='smart_diagnostic_api'),
    path('api/obd-simulator/', OBDSimulatorAPIView.as_view(), name='obd_simulator'),
    path('api/obd-data/', OBDDeviceDataAPIView.as_view(), name='obd_data'),
]