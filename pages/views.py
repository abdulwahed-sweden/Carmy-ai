from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def home(request):
    """View for the home page"""
    context = {}
    
    # If user is authenticated, get their recent diagnostics
    if request.user.is_authenticated:
        try:
            # Import here to avoid circular imports
            from accounts.models import DiagnosticHistory
            
            # Get recent diagnostics for the user
            recent_diagnostics = DiagnosticHistory.objects.filter(
                vehicle__user=request.user
            ).order_by('-date')[:4]
            
            context['recent_diagnostics'] = recent_diagnostics
        except (ImportError, AttributeError):
            # Fallback if the model doesn't exist or has different structure
            context['recent_diagnostics'] = []
    
    return render(request, 'pages/home.html', context)


def about(request):
    """View for the about page"""
    return render(request, 'pages/about.html')


def contact(request):
    """View for the contact page"""
    return render(request, 'pages/contact.html')


def faq(request):
    """View for the FAQ page"""
    faqs = [
        {
            'question': 'What is an OBD-II scanner?',
            'answer': 'An OBD-II scanner is a device that connects to your car\'s diagnostic port to read error codes and monitor vehicle performance.'
        },
        {
            'question': 'How do I find my car\'s OBD-II port?',
            'answer': 'The OBD-II port is typically located under the dashboard on the driver\'s side, often near the steering column.'
        },
        {
            'question': 'What can I do with this website?',
            'answer': 'You can look up error codes, track your vehicle\'s maintenance history, and get diagnostic information for your car.'
        },
        {
            'question': 'Do I need special hardware to use this system?',
            'answer': 'For basic features like looking up codes, no. For real-time diagnostics, you\'ll need an OBD-II scanner that can connect to your phone or computer.'
        },
        {
            'question': 'Are all cars compatible?',
            'answer': 'Most vehicles manufactured after 1996 use the OBD-II standard and are compatible with our system.'
        },
    ]
    return render(request, 'pages/faq.html', {'faqs': faqs})


def terms(request):
    """View for the terms of service page"""
    return render(request, 'pages/terms.html')


def privacy(request):
    """View for the privacy policy page"""
    return render(request, 'pages/privacy.html')