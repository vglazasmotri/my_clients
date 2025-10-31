"""
Конфигурация pytest для проекта.

Фикстуры и настройки для тестирования Django приложения.
"""
import pytest
from django.test import RequestFactory
from clients.models import DataSource, Client


@pytest.fixture
def factory():
    """
    Фикстура для создания RequestFactory.
    
    Используется для тестирования views без запуска сервера.
    """
    return RequestFactory()


@pytest.fixture
def data_source(db):
    """
    Фикстура для создания тестового источника данных.
    
    Создает объект DataSource в базе данных для использования в тестах.
    """
    return DataSource.objects.create(name="Test Data Source")


@pytest.fixture
def client_instance(db, data_source):
    """
    Фикстура для создания тестового клиента.
    
    Создает полный объект Client со всеми полями для использования в тестах.
    """
    return Client.objects.create(
        full_name="ООО Тестовый Клиент",
        short_name="ТестКлиент",
        inn="123456789012",
        kpp="123456789",
        ogrn="1234567890123",
        address="г. Москва, ул. Тестовая, д. 1",
        okved="62.01",
        reg_date="2020-01-01",
        authorized_capital=10000.00,
        status=Client.StatusChoices.ACTIVE,
        data_source=data_source
    )


@pytest.fixture
def multiple_clients(db, data_source):
    """
    Фикстура для создания нескольких тестовых клиентов.
    
    Создает 5 клиентов для тестирования списков и фильтрации.
    """
    clients = []
    for i in range(5):
        client = Client.objects.create(
            full_name=f"ООО Клиент {i+1}",
            short_name=f"Клиент{i+1}",
            inn=f"1234567890{i:02d}",
            kpp="123456789",
            ogrn=f"123456789012{i:01d}",
            address=f"г. Москва, ул. Тестовая, д. {i+1}",
            okved="62.01",
            reg_date="2020-01-01",
            authorized_capital=10000.00 * (i+1),
            status=Client.StatusChoices.ACTIVE if i % 2 == 0 else Client.StatusChoices.LIQUIDATED,
            data_source=data_source
        )
        clients.append(client)
    return clients

