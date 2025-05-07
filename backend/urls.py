from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin URLs
    path('admin/', admin.site.urls),
    
    # Main app URLs
    path('', include('pages.urls')),  # Root URL for pages app
    path('accounts/', include('accounts.urls')),
    
    # Car Diagnostics URLs - Frontend and API
    path('diagnostics/', include('car_diagnostics.urls')),
]

# Add media URL configuration for development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)