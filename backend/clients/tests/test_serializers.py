"""
Тесты для сериализаторов Client и DataSource.

Проверяют сериализацию, десериализацию и валидацию данных.
"""
import pytest
from datetime import date
from rest_framework.exceptions import ValidationError as DRFValidationError
from clients.models import Client, DataSource
from clients.serializers import ClientSerializer, DataSourceSerializer


class TestDataSourceSerializer:
    """
    Тесты для сериализатора DataSource.
    
    Проверяет сериализацию и десериализацию источников данных.
    """
    
    def test_serialize_data_source(self, data_source):
        """
        Тест: Сериализация объекта DataSource.
        
        Arrange: Создание объекта DataSource
        Act: Сериализация объекта
        Assert: Проверка всех полей в результатах
        """
        # Arrange
        serializer = DataSourceSerializer(instance=data_source)
        
        # Act
        data = serializer.data
        
        # Assert
        assert 'id' in data
        assert 'name' in data
        assert 'created_at' in data
        assert 'updated_at' in data
        assert data['name'] == data_source.name
    
    def test_deserialize_data_source(self, db):
        """
        Тест: Десериализация валидных данных DataSource.
        
        Arrange: Подготовка валидных данных
        Act: Десериализация и сохранение
        Assert: Проверка создания объекта в БД
        """
        # Arrange
        valid_data = {'name': 'Новый источник'}
        
        # Act
        serializer = DataSourceSerializer(data=valid_data)
        assert serializer.is_valid(), serializer.errors
        data_source = serializer.save()
        
        # Assert
        assert data_source.id is not None
        assert data_source.name == 'Новый источник'
        assert DataSource.objects.count() == 1


class TestClientSerializer:
    """
    Тесты для сериализатора Client.
    
    Проверяет сериализацию, десериализацию и валидацию клиентов.
    """
    
    def test_serialize_client(self, client_instance):
        """
        Тест: Сериализация объекта Client со всеми полями.
        
        Arrange: Создание полного объекта Client
        Act: Сериализация объекта
        Assert: Проверка всех полей в результатах
        """
        # Arrange
        serializer = ClientSerializer(instance=client_instance)
        
        # Act
        data = serializer.data
        
        # Assert - проверка всех полей
        assert 'id' in data
        assert 'full_name' in data
        assert 'short_name' in data
        assert 'inn' in data
        assert 'kpp' in data
        assert 'ogrn' in data
        assert 'address' in data
        assert 'okved' in data
        assert 'reg_date' in data
        assert 'authorized_capital' in data
        assert 'status' in data
        assert 'data_source' in data
        assert 'last_checked_at' in data
        assert 'created_at' in data
        assert 'updated_at' in data
        
        # Проверка значений
        assert data['full_name'] == client_instance.full_name
        assert data['inn'] == client_instance.inn
        assert data['status'] == client_instance.status
    
    def test_deserialize_valid_client_data(self, data_source):
        """
        Тест: Десериализация валидных данных Client.
        
        Arrange: Подготовка валидных данных
        Act: Десериализация и сохранение
        Assert: Проверка создания объекта в БД
        """
        # Arrange
        valid_data = {
            'full_name': 'ООО Валидный Клиент',
            'short_name': 'ВалидКлиент',
            'inn': '123456789012',
            'kpp': '123456789',
            'ogrn': '1234567890123',
            'address': 'г. Москва, ул. Тестовая, д. 1',
            'okved': '62.01',
            'reg_date': '2020-01-01',
            'authorized_capital': '10000.00',
            'status': 'active',
            'data_source': data_source.id
        }
        
        # Act
        serializer = ClientSerializer(data=valid_data)
        assert serializer.is_valid(), serializer.errors
        client = serializer.save()
        
        # Assert
        assert client.id is not None
        assert client.full_name == 'ООО Валидный Клиент'
        assert client.inn == '123456789012'
        assert Client.objects.count() == 1
    
    def test_validate_inn_wrong_length(self, data_source):
        """
        Тест: Валидация ИНН - неверная длина (не 10 или 12 символов).
        
        Arrange: Подготовка данных с невалидным ИНН
        Act: Попытка десериализации
        Assert: Ожидается ValidationError
        """
        # Arrange
        invalid_data = {
            'full_name': 'ООО Тест',
            'short_name': 'Тест',
            'inn': '123456789',  # Неправильная длина (9 символов)
            'status': 'active',
            'data_source': data_source.id
        }
        
        # Act
        serializer = ClientSerializer(data=invalid_data)
        
        # Assert
        assert not serializer.is_valid()
        assert 'inn' in serializer.errors
    
    def test_validate_inn_valid_lengths(self, data_source):
        """
        Тест: Валидация ИНН - валидные длины (10 и 12 символов).
        
        Arrange: Подготовка данных с валидным ИНН
        Act: Попытка десериализации
        Assert: Должно быть валидно
        """
        # Arrange - ИНН из 10 цифр (ИП)
        data_10_digits = {
            'full_name': 'ИП Тест',
            'short_name': 'ИП',
            'inn': '1234567890',
            'status': 'active',
            'data_source': data_source.id
        }
        
        # Act
        serializer_10 = ClientSerializer(data=data_10_digits)
        
        # Assert
        assert serializer_10.is_valid()
        
        # Arrange - ИНН из 12 цифр (организация)
        data_12_digits = {
            'full_name': 'ООО Тест',
            'short_name': 'Тест',
            'inn': '123456789012',
            'status': 'active',
            'data_source': data_source.id
        }
        
        # Act
        serializer_12 = ClientSerializer(data=data_12_digits)
        
        # Assert
        assert serializer_12.is_valid()
    
    def test_validate_inn_non_digits(self, data_source):
        """
        Тест: Валидация ИНН - не цифры.
        
        Arrange: Подготовка данных с буквами в ИНН
        Act: Попытка десериализации
        Assert: Ожидается ValidationError
        """
        # Arrange
        invalid_data = {
            'full_name': 'ООО Тест',
            'short_name': 'Тест',
            'inn': '12345678901a',  # Буква вместо цифры
            'status': 'active',
            'data_source': data_source.id
        }
        
        # Act
        serializer = ClientSerializer(data=invalid_data)
        
        # Assert
        assert not serializer.is_valid()
        assert 'inn' in serializer.errors
    
    def test_validate_kpp_wrong_length(self, data_source):
        """
        Тест: Валидация КПП - неверная длина (не 9 символов).
        
        Arrange: Подготовка данных с невалидным КПП
        Act: Попытка десериализации
        Assert: Ожидается ValidationError
        """
        # Arrange
        invalid_data = {
            'full_name': 'ООО Тест',
            'short_name': 'Тест',
            'inn': '123456789012',
            'kpp': '12345678',  # Неправильная длина (8 символов)
            'status': 'active',
            'data_source': data_source.id
        }
        
        # Act
        serializer = ClientSerializer(data=invalid_data)
        
        # Assert
        assert not serializer.is_valid()
        assert 'kpp' in serializer.errors
    
    def test_validate_ogrn_wrong_length(self, data_source):
        """
        Тест: Валидация ОГРН - неверная длина (не 13 или 15 символов).
        
        Arrange: Подготовка данных с невалидным ОГРН
        Act: Попытка десериализации
        Assert: Ожидается ValidationError
        """
        # Arrange
        invalid_data = {
            'full_name': 'ООО Тест',
            'short_name': 'Тест',
            'inn': '123456789012',
            'ogrn': '123456789012',  # Неправильная длина (12 символов)
            'status': 'active',
            'data_source': data_source.id
        }
        
        # Act
        serializer = ClientSerializer(data=invalid_data)
        
        # Assert
        assert not serializer.is_valid()
        assert 'ogrn' in serializer.errors
    
    def test_validate_ogrn_valid_lengths(self, data_source):
        """
        Тест: Валидация ОГРН - валидные длины (13 и 15 символов).
        
        Arrange: Подготовка данных с валидным ОГРН
        Act: Попытка десериализации
        Assert: Должно быть валидно
        """
        # Arrange - ОГРН из 13 цифр (юрлицо)
        data_13_digits = {
            'full_name': 'ООО Тест',
            'short_name': 'Тест',
            'inn': '123456789012',
            'ogrn': '1234567890123',
            'status': 'active',
            'data_source': data_source.id
        }
        
        # Act
        serializer_13 = ClientSerializer(data=data_13_digits)
        
        # Assert
        assert serializer_13.is_valid()
        
        # Arrange - ОГРН из 15 цифр (ИП)
        data_15_digits = {
            'full_name': 'ИП Тест',
            'short_name': 'ИП',
            'inn': '1234567890',
            'ogrn': '123456789012345',
            'status': 'active',
            'data_source': data_source.id
        }
        
        # Act
        serializer_15 = ClientSerializer(data=data_15_digits)
        
        # Assert
        assert serializer_15.is_valid()
    
    def test_validate_invalid_status(self, data_source):
        """
        Тест: Валидация статуса - неверное значение.
        
        Arrange: Подготовка данных с невалидным статусом
        Act: Попытка десериализации
        Assert: Ожидается ValidationError
        """
        # Arrange
        invalid_data = {
            'full_name': 'ООО Тест',
            'short_name': 'Тест',
            'inn': '123456789012',
            'status': 'invalid_status',  # Неправильный статус
            'data_source': data_source.id
        }
        
        # Act
        serializer = ClientSerializer(data=invalid_data)
        
        # Assert
        assert not serializer.is_valid()
        assert 'status' in serializer.errors
    
    def test_required_inn_or_ogrn(self, data_source):
        """
        Тест: Проверка, что необходимо заполнить хотя бы одно из полей: inn или ogrn.
        
        Arrange: Подготовка данных без inn и ogrn
        Act: Попытка десериализации
        Assert: Ожидается ValidationError
        """
        # Arrange
        invalid_data = {
            'full_name': 'ООО Тест',
            'short_name': 'Тест',
            'status': 'active',
            'data_source': data_source.id
        }
        
        # Act
        serializer = ClientSerializer(data=invalid_data)
        
        # Assert
        assert not serializer.is_valid()
        assert 'inn' in serializer.errors or 'non_field_errors' in serializer.errors
    
    def test_create_client_only_with_inn(self, data_source):
        """
        Тест: Создание клиента только с ИНН без ОГРН.
        
        Arrange: Подготовка данных только с ИНН
        Act: Попытка десериализации и сохранения
        Assert: Клиент успешно создан
        """
        # Arrange
        valid_data = {
            'inn': '123456789012',
            'data_source': data_source.id,
            'status': 'active'
        }
        
        # Act
        serializer = ClientSerializer(data=valid_data)
        
        # Assert
        assert serializer.is_valid()
        client = serializer.save()
        assert client.inn == '123456789012'
        assert client.ogrn is None
    
    def test_create_client_only_with_ogrn(self, data_source):
        """
        Тест: Создание клиента только с ОГРН без ИНН.
        
        Arrange: Подготовка данных только с ОГРН
        Act: Попытка десериализации и сохранения
        Assert: Клиент успешно создан
        """
        # Arrange
        valid_data = {
            'ogrn': '1234567890123',
            'data_source': data_source.id,
            'status': 'active'
        }
        
        # Act
        serializer = ClientSerializer(data=valid_data)
        
        # Assert
        assert serializer.is_valid()
        client = serializer.save()
        assert client.ogrn == '1234567890123'
        assert client.inn is None
    
    def test_required_fields_status(self, data_source):
        """
        Тест: Проверка поля status с default значением.
        
        Arrange: Подготовка данных без status
        Act: Попытка десериализации
        Assert: Должен быть принят, т.к. status имеет default
        """
        # Arrange
        valid_data = {
            'full_name': 'ООО Тест',
            'short_name': 'Тест',
            'inn': '123456789012',
            'data_source': data_source.id
        }
        
        # Act
        serializer = ClientSerializer(data=valid_data)
        serializer.is_valid()
        
        # Assert
        assert serializer.is_valid()
        # Проверяем, что без status используется default
        saved_client = serializer.save()
        assert saved_client.status == 'active'  # default значение
    
    def test_read_only_fields_id(self, data_source):
        """
        Тест: Поле id только для чтения.
        
        Arrange: Создание клиента и подготовка данных с id
        Act: Попытка обновления через сериализатор
        Assert: id игнорируется при обновлении
        """
        # Arrange
        client = Client.objects.create(
            full_name='ООО Тест',
            short_name='Тест',
            inn='111111111111',
            status=Client.StatusChoices.ACTIVE,
            data_source=data_source
        )
        
        update_data = {
            'id': 99999,  # Попытка изменить id
            'full_name': 'ООО Обновлен',
            'short_name': 'Обновлен',
            'inn': '111111111111',
            'status': 'active',
            'data_source': data_source.id
        }
        
        # Act
        serializer = ClientSerializer(instance=client, data=update_data)
        assert serializer.is_valid()
        updated_client = serializer.save()
        
        # Assert - id не должен был измениться
        assert updated_client.id == client.id
        assert updated_client.full_name == 'ООО Обновлен'
    
    def test_read_only_fields_timestamps(self, client_instance, data_source):
        """
        Тест: Поля timestamps только для чтения.
        
        Arrange: Создание клиента и получение его timestamps
        Act: Попытка обновить timestamps через API данные
        Assert: timestamps должны игнорироваться
        """
        # Arrange
        old_created = client_instance.created_at
        old_updated = client_instance.updated_at
        
        update_data = {
            'full_name': client_instance.full_name,
            'short_name': client_instance.short_name,
            'inn': client_instance.inn,
            'status': client_instance.status,
            'data_source': data_source.id,
            'created_at': '1900-01-01T00:00:00Z',  # Попытка изменить
            'updated_at': '1900-01-01T00:00:00Z'   # Попытка изменить
        }
        
        # Act
        serializer = ClientSerializer(instance=client_instance, data=update_data)
        assert serializer.is_valid()
        updated_client = serializer.save()
        
        # Assert - timestamps не должны были измениться извне
        assert updated_client.created_at == old_created

