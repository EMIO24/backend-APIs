"""
URL configuration for podcast project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# In your project's urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings # Import settings
from django.conf.urls.static import static # Import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('Users.urls')), # Replace 'your_auth_app'
    path('api/', include('category.urls')), # Replace 'your_podcast_app' and include its urls
    path('api/', include('episodes_app.urls')), # Mandatory: Include Task 3 urls here
    path('api/', include('subscriptions.urls')),        # Mandatory: Include Task 4 urls here
    # ... other project urls
]

# Add this only in development for serving media files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)