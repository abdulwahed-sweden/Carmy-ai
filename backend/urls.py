from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    # المسارات الموجودة
    path('admin/', admin.site.urls),
    path('', include('pages.urls')),  # Root URL for pages app
    path('accounts/', include('accounts.urls')),
    #path('posts/', include('posts.urls')),
    
    # المسارات الجديدة
    path('api/diagnostics/', include('car_diagnostics.urls')),
]
