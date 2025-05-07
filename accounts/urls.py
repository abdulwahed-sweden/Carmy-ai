from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication URLs
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Profile URLs
    path('profile/', views.profile, name='profile'),
    
    # Vehicle management URLs
    path('vehicles/', views.vehicles, name='vehicles'),
    path('vehicles/add/', views.add_vehicle, name='add_vehicle'),
    path('vehicles/<int:vehicle_id>/edit/', views.edit_vehicle, name='edit_vehicle'),
    path('vehicles/<int:vehicle_id>/delete/', views.delete_vehicle, name='delete_vehicle'),
    
    # Diagnostic history URLs
    path('diagnostics/', views.diagnostic_history, name='history'),
    path('diagnostics/<int:diagnostic_id>/', views.diagnostic_detail, name='diagnostic_detail'),
    
    # Maintenance records URLs
    path('vehicles/<int:vehicle_id>/maintenance/', views.maintenance_records, name='maintenance_records'),
    path('vehicles/<int:vehicle_id>/maintenance/add/', views.add_maintenance, name='add_maintenance'),
]