"""
Тесты для API эндпоинтов Client.

Проверяют все CRUD операции через HTTP запросы.
"""
import pytest
from datetime import date
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from clients.models import Client, DataSource


@pytest.fixture
def api_client():
    """
    Фикстура для создания APIClient.
    
    Используется для тестирования API эндпоинтов.
    """
    return APIClient()


@pytest.fixture
def client_payload(data_source):
    """
    Фикстура для тестовых данных клиента.
    
    Возвращает валидные данные для создания клиента через API.
    """
    return {
        'full_name': 'ООО API Тест',
        'short_name': 'APITest',
        'inn': '123456789012',
        'kpp': '123456789',
        'ogrn': '1234567890123',
        'address': 'г. Москва, ул. API Тестовая, д. 1',
        'okved': '62.01',
        'reg_date': '2020-01-01',
        'authorized_capital': '10000.00',
        'status': 'active',
        'data_source': data_source.id
    }


class TestClientListAPI:
    """
    Тесты для API списка клиентов (GET /api/clients/).
    
    Проверяет получение списка всех клиентов.
    """
    
    @pytest.mark.django_db
    def test_list_clients_empty(self, api_client):
        """
        Тест: Получение пустого списка клиентов.
        
        Arrange: Пустая база данных
        Act: GET запрос на список клиентов
        Assert: 200 OK, пустой список
        """
        # Arrange & Act
        url = reverse('client-list')
        response = api_client.get(url)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert len(response.data['results']) == 0
    
    def test_list_clients_with_data(self, api_client, multiple_clients):
        """
        Тест: Получение списка клиентов с данными.
        
        Arrange: Создание нескольких клиентов
        Act: GET запрос на список клиентов
        Assert: 200 OK, корректная структура JSON
        """
        # Arrange & Act
        url = reverse('client-list')
        response = api_client.get(url)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert len(response.data['results']) == 5
        
        # Проверка структуры первого клиента
        first_client = response.data['results'][0]
        assert 'id' in first_client
        assert 'full_name' in first_client
        assert 'inn' in first_client
        assert 'status' in first_client
        assert 'data_source' in first_client


class TestClientCreateAPI:
    """
    Тесты для API создания клиента (POST /api/clients/).
    
    Проверяет создание нового клиента.
    """
    
    def test_create_client_valid(self, api_client, client_payload):
        """
        Тест: Создание клиента с валидными данными.
        
        Arrange: Подготовка валидных данных
        Act: POST запрос на создание клиента
        Assert: 201 Created, клиент создан в БД
        """
        # Arrange & Act
        url = reverse('client-list')
        response = api_client.post(url, client_payload, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert 'id' in response.data
        assert response.data['full_name'] == client_payload['full_name']
        assert response.data['inn'] == client_payload['inn']
        
        # Проверка в БД
        assert Client.objects.count() == 1
        assert Client.objects.filter(inn=client_payload['inn']).exists()
    
    def test_create_client_invalid_data(self, api_client, client_payload, data_source):
        """
        Тест: Создание клиента с невалидными данными.
        
        Arrange: Подготовка невалидных данных (неправильный ИНН)
        Act: POST запрос на создание
        Assert: 400 Bad Request, ошибки валидации
        """
        # Arrange
        client_payload['inn'] = '12345'  # Неправильная длина
        
        # Act
        url = reverse('client-list')
        response = api_client.post(url, client_payload, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'inn' in response.data
        
        # Проверка, что в БД ничего не создано
        assert Client.objects.count() == 0
    
    @pytest.mark.django_db
    def test_create_client_missing_inn_and_ogrn(self, api_client, data_source):
        """
        Тест: Создание клиента без ИНН и ОГРН.
        
        Arrange: Подготовка данных без обязательных полей ИНН и ОГРН
        Act: POST запрос на создание
        Assert: 400 Bad Request, ошибки для обязательных полей
        """
        # Arrange
        incomplete_data = {
            'short_name': 'Неполный',
            'data_source': data_source.id
        }
        
        # Act
        url = reverse('client-list')
        response = api_client.post(url, incomplete_data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        # Проверяем, что ошибка связана с отсутствием ИНН или ОГРН
        assert 'inn' in response.data or 'ogrn' in response.data
    
    @pytest.mark.django_db
    def test_create_client_only_with_inn(self, api_client, data_source):
        """
        Тест: Создание клиента только с ИНН.
        
        Arrange: Подготовка данных только с ИНН
        Act: POST запрос на создание
        Assert: 201 Created, клиент создан
        """
        # Arrange
        data = {
            'inn': '123456789012',
            'data_source': data_source.id
        }
        
        # Act
        url = reverse('client-list')
        response = api_client.post(url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['inn'] == '123456789012'
        assert Client.objects.count() == 1


class TestClientRetrieveAPI:
    """
    Тесты для API получения клиента (GET /api/clients/{id}/).
    
    Проверяет получение одного клиента по ID.
    """
    
    def test_retrieve_client_existing(self, api_client, client_instance):
        """
        Тест: Получение существующего клиента.
        
        Arrange: Создание клиента
        Act: GET запрос на получение клиента
        Assert: 200 OK, все поля присутствуют
        """
        # Arrange & Act
        url = reverse('client-detail', kwargs={'id': client_instance.id})
        response = api_client.get(url)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == client_instance.id
        assert response.data['full_name'] == client_instance.full_name
        assert response.data['inn'] == client_instance.inn
        assert 'created_at' in response.data
    
    @pytest.mark.django_db
    def test_retrieve_client_not_found(self, api_client):
        """
        Тест: Получение несуществующего клиента.
        
        Arrange: Пустая база данных
        Act: GET запрос на несуществующий ID
        Assert: 404 Not Found
        """
        # Arrange & Act
        url = reverse('client-detail', kwargs={'id': 99999})
        response = api_client.get(url)
        
        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestClientUpdateAPI:
    """
    Тесты для API обновления клиента (PUT /api/clients/{id}/).
    
    Проверяет полное обновление клиента.
    """
    
    def test_update_client_full(self, api_client, client_instance, data_source):
        """
        Тест: Полное обновление клиента (PUT).
        
        Arrange: Создание клиента и новых данных
        Act: PUT запрос на обновление
        Assert: 200 OK, данные обновлены в БД
        """
        # Arrange
        update_data = {
            'full_name': 'ООО Обновленный',
            'short_name': 'Обновлен',
            'inn': '111111111111',
            'kpp': '111111111',
            'ogrn': '1111111111111',
            'address': 'Новый адрес',
            'okved': '63.11',
            'reg_date': '2021-01-01',
            'authorized_capital': '20000.00',
            'status': 'liquidated',
            'data_source': data_source.id
        }
        
        # Act
        url = reverse('client-detail', kwargs={'id': client_instance.id})
        response = api_client.put(url, update_data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['full_name'] == 'ООО Обновленный'
        assert response.data['inn'] == '111111111111'
        assert response.data['status'] == 'liquidated'
        
        # Проверка в БД
        client_instance.refresh_from_db()
        assert client_instance.full_name == 'ООО Обновленный'
        assert client_instance.inn == '111111111111'
    
    @pytest.mark.django_db
    def test_put_client_without_inn_and_ogrn(self, api_client, client_instance, data_source):
        """
        Тест: Полное обновление клиента (PUT) без ИНН и ОГРН.
        
        Arrange: Создание клиента
        Act: PUT запрос без ИНН и ОГРН
        Assert: 400 Bad Request, ошибка валидации
        """
        # Arrange
        update_data = {
            'full_name': 'ООО Без ИНН',
            'short_name': 'Без ИНН',
            'address': 'Новый адрес',
            'status': 'active',
            'data_source': data_source.id
        }
        
        # Act
        url = reverse('client-detail', kwargs={'id': client_instance.id})
        response = api_client.put(url, update_data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'inn' in response.data
        assert 'ogrn' in response.data


class TestClientPartialUpdateAPI:
    """
    Тесты для API частичного обновления (PATCH /api/clients/{id}/).
    
    Проверяет частичное обновление клиента.
    """
    
    def test_partial_update_client(self, api_client, client_instance):
        """
        Тест: Частичное обновление клиента (PATCH).
        
        Arrange: Создание клиента
        Act: PATCH запрос с одним полем
        Assert: 200 OK, только это поле обновлено
        """
        # Arrange
        partial_data = {
            'full_name': 'ООО Частично Обновленный'
        }
        
        # Act
        url = reverse('client-detail', kwargs={'id': client_instance.id})
        response = api_client.patch(url, partial_data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['full_name'] == 'ООО Частично Обновленный'
        
        # Проверка, что другие поля не изменились
        client_instance.refresh_from_db()
        assert client_instance.inn == '123456789012'  # Не изменился
        assert client_instance.full_name == 'ООО Частично Обновленный'


class TestClientDeleteAPI:
    """
    Тесты для API удаления клиента (DELETE /api/clients/{id}/).
    
    Проверяет удаление клиента.
    """
    
    def test_delete_client_existing(self, api_client, client_instance):
        """
        Тест: Удаление существующего клиента.
        
        Arrange: Создание клиента
        Act: DELETE запрос
        Assert: 204 No Content, клиент удален из БД
        """
        # Arrange
        client_id = client_instance.id
        
        # Act
        url = reverse('client-detail', kwargs={'id': client_id})
        response = api_client.delete(url)
        
        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Проверка в БД
        assert not Client.objects.filter(id=client_id).exists()
        assert Client.objects.count() == 0
    
    @pytest.mark.django_db
    def test_delete_client_not_found(self, api_client):
        """
        Тест: Удаление несуществующего клиента.
        
        Arrange: Пустая база данных
        Act: DELETE запрос на несуществующий ID
        Assert: 404 Not Found
        """
        # Arrange & Act
        url = reverse('client-detail', kwargs={'id': 99999})
        response = api_client.delete(url)
        
        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND

