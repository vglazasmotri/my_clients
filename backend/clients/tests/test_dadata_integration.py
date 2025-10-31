"""
Тесты для интеграции с DaData API.

Проверяют получение данных о компании по ИНН из DaData.
"""
import pytest
from unittest.mock import patch, MagicMock
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from clients.models import Client, DataSource
from clients.services.dadata_service import DaDataService


@pytest.fixture
def api_client():
    """
    Фикстура для создания APIClient.
    
    Используется для тестирования API эндпоинтов.
    """
    return APIClient()


@pytest.fixture
def data_source_dadata(db):
    """
    Фикстура для создания источника данных DaData.
    
    Создает объект DataSource с названием DaData для тестов.
    """
    return DataSource.objects.create(name="DaData")


class TestDaDataService:
    """
    Тесты для сервиса DaDataService.
    
    Проверяют получение данных о компании из DaData API.
    """
    
    def test_get_company_data_by_inn_success(self, data_source_dadata):
        """
        Тест: Успешное получение данных компании по ИНН.
        
        Arrange: Подготовка мок-ответа от DaData
        Act: Вызов сервиса с валидным ИНН
        Assert: Проверка всех полей в ответе
        """
        # Arrange - мок-ответ от DaData API
        mock_response = {
            "suggestions": [
                {
                    "value": "ПАО СБЕРБАНК",
                    "data": {
                        "inn": "770708389312",
                        "kpp": "770401001",
                        "ogrn": "1027700132195",
                        "name": {
                            "full_with_opf": "ПУБЛИЧНОЕ АКЦИОНЕРНОЕ ОБЩЕСТВО \"СБЕРБАНК\"",
                            "short_with_opf": "ПАО СБЕРБАНК",
                            "full": "СБЕРБАНК",
                            "short": "СБЕРБАНК"
                        },
                        "address": {
                            "unrestricted_value": "г Москва, ул Вавилова, д 19"
                        },
                        "okved": "64.19",
                        "okved_detailed": [
                            {
                                "code": "64.19.1",
                                "name": "Денежное посредничество"
                            }
                        ],
                        "state": {
                            "status": "ACTIVE",
                            "registration_date": 1041278400000,
                            "liquidation_date": None
                        },
                        "capital": {
                            "value": 6776084694.0
                        }
                    }
                }
            ]
        }
        
        # Act - вызов сервиса с моком
        with patch('clients.services.dadata_service.requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = mock_response
            
            service = DaDataService()
            # Устанавливаем тестовый API ключ
            service.api_key = 'test_api_key'
            result = service.get_company_data_by_inn("770708389312", data_source_dadata.id)
        
        # Assert - проверка всех полей
        assert result is not None
        assert result['full_name'] == "ПУБЛИЧНОЕ АКЦИОНЕРНОЕ ОБЩЕСТВО \"СБЕРБАНК\""
        assert result['short_name'] == "ПАО СБЕРБАНК"
        assert result['inn'] == "770708389312"
        assert result['kpp'] == "770401001"
        assert result['ogrn'] == "1027700132195"
        assert result['address'] == "г Москва, ул Вавилова, д 19"
        assert result['okved'] == "64.19"
        assert result['authorized_capital'] == "6776084694.00"
        assert result['reg_date'] == "2002-12-30"  # Преобразование timestamp
    
    def test_get_company_data_by_inn_not_found(self, data_source_dadata):
        """
        Тест: Компания не найдена в DaData.
        
        Arrange: Подготовка пустого ответа
        Act: Вызов сервиса с несуществующим ИНН
        Assert: Возвращается None
        """
        # Arrange
        mock_response = {"suggestions": []}
        
        # Act
        with patch('clients.services.dadata_service.requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = mock_response
            
            service = DaDataService()
            service.api_key = 'test_api_key'
            result = service.get_company_data_by_inn("999999999999", data_source_dadata.id)
        
        # Assert
        assert result is None
    
    def test_get_company_data_by_inn_api_error(self, data_source_dadata):
        """
        Тест: Ошибка при запросе к DaData API.
        
        Arrange: Подготовка ошибочного ответа
        Act: Вызов сервиса
        Assert: Возвращается None при ошибке
        """
        # Arrange
        mock_response = {"error": "Invalid API key"}
        
        # Act
        with patch('clients.services.dadata_service.requests.post') as mock_post:
            mock_post.return_value.status_code = 403
            mock_post.return_value.json.return_value = mock_response
            
            service = DaDataService()
            service.api_key = 'test_api_key'
            result = service.get_company_data_by_inn("770708389312", data_source_dadata.id)
        
        # Assert
        assert result is None
    
    def test_get_company_data_by_inn_network_error(self, data_source_dadata):
        """
        Тест: Сетевая ошибка при запросе к DaData API.
        
        Arrange: Подготовка исключения
        Act: Вызов сервиса
        Assert: Возвращается None при сетевой ошибке
        """
        # Arrange & Act
        with patch('clients.services.dadata_service.requests.post') as mock_post:
            mock_post.side_effect = Exception("Network error")
            
            service = DaDataService()
            service.api_key = 'test_api_key'
            result = service.get_company_data_by_inn("770708389312", data_source_dadata.id)
        
        # Assert
        assert result is None


class TestDaDataAPIIntegration:
    """
    Тесты для API эндпоинтов с интеграцией DaData.
    
    Проверяют создание клиента через API с автозаполнением из DaData.
    """
    
    def test_create_client_with_dadata_fetch(self, api_client, data_source_dadata):
        """
        Тест: Создание клиента с получением данных из DaData.
        
        Arrange: Подготовка мок-ответа от DaData
        Act: Создание клиента только с ИНН через API
        Assert: Клиент создан со всеми полями из DaData
        """
        # Arrange - мок-ответ от DaData
        mock_response = {
            "suggestions": [
                {
                    "value": "ООО ТЕСТОВАЯ КОМПАНИЯ",
                    "data": {
                        "inn": "123456789012",
                        "kpp": "123456789",
                        "ogrn": "1234567890123",
                        "name": {
                            "full_with_opf": "ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ \"ТЕСТОВАЯ КОМПАНИЯ\"",
                            "short_with_opf": "ООО ТЕСТОВАЯ КОМПАНИЯ"
                        },
                        "address": {
                            "unrestricted_value": "г Москва, ул Тестовая, д 1"
                        },
                        "okved": "62.01",
                        "state": {
                            "status": "ACTIVE",
                            "registration_date": 946684800000
                        },
                        "capital": {
                            "value": 10000.0
                        }
                    }
                }
            ]
        }
        
        # Act - создание клиента через API с моком DaData
        with patch('clients.services.dadata_service.requests.post') as mock_post, \
             patch('clients.services.dadata_service.os.environ.get', return_value='test_api_key'):
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = mock_response
            
            response = api_client.post(
                '/api/clients/',
                {
                    'inn': '123456789012',
                    'data_source': data_source_dadata.id
                },
                format='json'
            )
        
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['full_name'] == 'ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ "ТЕСТОВАЯ КОМПАНИЯ"'
        assert response.data['short_name'] == 'ООО ТЕСТОВАЯ КОМПАНИЯ'
        assert response.data['inn'] == '123456789012'
        assert response.data['kpp'] == '123456789'
        assert response.data['ogrn'] == '1234567890123'
        
        # Проверка в БД
        assert Client.objects.count() == 1
        client = Client.objects.first()
        assert client.full_name == 'ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ "ТЕСТОВАЯ КОМПАНИЯ"'
        assert client.data_source == data_source_dadata
    
    def test_create_client_without_dadata_when_service_fails(self, api_client, data_source_dadata):
        """
        Тест: Создание клиента без DaData при ошибке сервиса.
        
        Arrange: Подготовка ошибочного ответа от DaData
        Act: Создание клиента через API
        Assert: Клиент создается успешно, т.к. теперь нет обязательных полей
        """
        # Arrange
        mock_response = {"suggestions": []}
        
        # Act
        with patch('clients.services.dadata_service.requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = mock_response
            
            response = api_client.post(
                '/api/clients/',
                {
                    'inn': '123456789012',
                    'data_source': data_source_dadata.id
                },
                format='json'
            )
        
        # Assert
        # Теперь клиент создается успешно, т.к. ИНН заполнен
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['inn'] == '123456789012'
        assert Client.objects.count() == 1

