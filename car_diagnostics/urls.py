from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CarViewSet, ErrorCodeViewSet

router = DefaultRouter()
router.register(r'cars', CarViewSet)
router.register(r'error-codes', ErrorCodeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]