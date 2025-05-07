from django.shortcuts import render

def home(request):
    """View for the home page"""
    context = {}
    
    # If user is authenticated, get their recent diagnostics
    if request.user.is_authenticated:
        # This is just a placeholder - adjust based on your models
        from car_diagnostics.models import DiagnosticHistory
        context['recent_diagnostics'] = DiagnosticHistory.objects.filter(
            vehicle__user=request.user
        ).order_by('-date')[:4]
    
    return render(request, 'pages/home.html', context)

def about(request):
    """View for the about page"""
    return render(request, 'pages/about.html')

def contact(request):
    """View for the contact page"""
    return render(request, 'pages/contact.html')