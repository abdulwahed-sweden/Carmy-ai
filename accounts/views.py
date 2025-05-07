from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile, UserVehicle, DiagnosticHistory, MaintenanceRecord
from .forms import (
    UserRegisterForm, UserUpdateForm, ProfileUpdateForm,
    UserVehicleForm, MaintenanceRecordForm
)

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('accounts:login')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'You have been logged in!')
            return redirect('pages:home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out!')
    return redirect('pages:home')

@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('accounts:profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def vehicles(request):
    user_vehicles = UserVehicle.objects.filter(user=request.user)
    return render(request, 'accounts/vehicles.html', {'vehicles': user_vehicles})

@login_required
def add_vehicle(request):
    if request.method == 'POST':
        form = UserVehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.user = request.user
            
            # If this vehicle is marked as primary, unset others
            if vehicle.is_primary:
                UserVehicle.objects.filter(user=request.user, is_primary=True).update(is_primary=False)
                
            vehicle.save()
            messages.success(request, 'Vehicle added successfully!')
            return redirect('accounts:vehicles')
    else:
        form = UserVehicleForm()
    return render(request, 'accounts/vehicle_form.html', {'form': form, 'title': 'Add Vehicle'})

@login_required
def edit_vehicle(request, vehicle_id):
    vehicle = get_object_or_404(UserVehicle, id=vehicle_id, user=request.user)
    
    if request.method == 'POST':
        form = UserVehicleForm(request.POST, instance=vehicle)
        if form.is_valid():
            # If this vehicle is being set as primary, unset others
            if form.cleaned_data.get('is_primary') and not vehicle.is_primary:
                UserVehicle.objects.filter(user=request.user, is_primary=True).update(is_primary=False)
                
            form.save()
            messages.success(request, 'Vehicle updated successfully!')
            return redirect('accounts:vehicles')
    else:
        form = UserVehicleForm(instance=vehicle)
    
    return render(request, 'accounts/vehicle_form.html', {
        'form': form,
        'title': 'Edit Vehicle',
        'vehicle': vehicle
    })

@login_required
def delete_vehicle(request, vehicle_id):
    vehicle = get_object_or_404(UserVehicle, id=vehicle_id, user=request.user)
    
    if request.method == 'POST':
        vehicle.delete()
        messages.success(request, 'Vehicle deleted successfully!')
        return redirect('accounts:vehicles')
    
    return render(request, 'accounts/delete_confirm.html', {
        'object': vehicle,
        'title': 'Delete Vehicle'
    })

@login_required
def diagnostic_history(request):
    # Get all vehicles belonging to the user
    user_vehicles = UserVehicle.objects.filter(user=request.user)
    
    # Get all diagnostic records for these vehicles
    diagnostics = DiagnosticHistory.objects.filter(
        vehicle__in=user_vehicles
    ).order_by('-date')
    
    return render(request, 'accounts/diagnostic_history.html', {'diagnostics': diagnostics})

@login_required
def diagnostic_detail(request, diagnostic_id):
    diagnostic = get_object_or_404(DiagnosticHistory, id=diagnostic_id, vehicle__user=request.user)
    return render(request, 'accounts/diagnostic_detail.html', {'diagnostic': diagnostic})

@login_required
def maintenance_records(request, vehicle_id):
    vehicle = get_object_or_404(UserVehicle, id=vehicle_id, user=request.user)
    records = MaintenanceRecord.objects.filter(vehicle=vehicle).order_by('-date')
    
    return render(request, 'accounts/maintenance_records.html', {
        'vehicle': vehicle,
        'records': records
    })

@login_required
def add_maintenance(request, vehicle_id):
    vehicle = get_object_or_404(UserVehicle, id=vehicle_id, user=request.user)
    
    if request.method == 'POST':
        form = MaintenanceRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.vehicle = vehicle
            record.save()
            messages.success(request, 'Maintenance record added successfully!')
            return redirect('accounts:maintenance_records', vehicle_id=vehicle.id)
    else:
        form = MaintenanceRecordForm()
    
    return render(request, 'accounts/maintenance_form.html', {
        'form': form,
        'vehicle': vehicle,
        'title': 'Add Maintenance Record'
    })