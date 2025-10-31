"""
URL конфигурация для приложения clients.

Маршрутизация API эндпоинтов для управления клиентами.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClientViewSet

# Создание роутера для автоматической генерации URL для ViewSet
router = DefaultRouter()
router.register(r'clients', ClientViewSet, basename='client')

urlpatterns = [
    # Подключение роутера
    path('', include(router.urls)),
]

