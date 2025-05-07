from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CarBrandViewSet, CarViewSet, ErrorCodeCategoryViewSet, 
    ErrorCodeViewSet, DiagnosticSearchViewSet
)

from .simulator import OBDSimulatorAPIView


router = DefaultRouter()
router.register(r'brands', CarBrandViewSet)
router.register(r'cars', CarViewSet)
router.register(r'error-categories', ErrorCodeCategoryViewSet)
router.register(r'error-codes', ErrorCodeViewSet)
router.register(r'diagnostic-search', DiagnosticSearchViewSet, basename='diagnostic-search')

urlpatterns = [
    path('', include(router.urls)),
    path('obd-simulator/', OBDSimulatorAPIView.as_view(), name='obd-simulator'),
]