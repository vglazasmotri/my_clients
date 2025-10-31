"""
URL configuration для проекта REST API.

Основной файл маршрутизации Django.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Админка Django
    path('admin/', admin.site.urls),
    
    # API эндпоинты
    path('api/', include('clients.urls')),
]

