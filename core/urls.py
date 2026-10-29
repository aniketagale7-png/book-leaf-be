"""
Main URL configuration for BookLeaf backend.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),  # All API endpoints go through /api/
]
