"""
Views для приложения clients.

API эндпоинты для управления клиентами.
"""
from rest_framework import viewsets
from .models import Client
from .serializers import ClientSerializer


class ClientViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления клиентами.
    
    Предоставляет полный CRUD функционал:
    - GET /api/clients/ - список всех клиентов
    - POST /api/clients/ - создание нового клиента
    - GET /api/clients/{id}/ - получение клиента по ID
    - PUT /api/clients/{id}/ - полное обновление клиента
    - PATCH /api/clients/{id}/ - частичное обновление клиента
    - DELETE /api/clients/{id}/ - удаление клиента
    """
    
    # QuerySet всех клиентов, отсортированный по дате создания
    queryset = Client.objects.all()
    
    # Сериализатор для преобразования данных
    serializer_class = ClientSerializer
    
    # Имя для поиска в URL (по умолчанию используется primary key)
    lookup_field = 'id'

