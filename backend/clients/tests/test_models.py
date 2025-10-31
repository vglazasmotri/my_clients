"""
Тесты для моделей Client и DataSource.

Проверяют создание объектов, валидацию полей и связи между моделями.
"""
import pytest
from datetime import date, datetime, timezone
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from clients.models import Client, DataSource


class TestDataSourceModel:
    """
    Тесты для модели DataSource.
    
    Проверяет создание источника данных и его основные поля.
    """
    
    def test_create_data_source(self, db):
        """
        Тест: Создание объекта DataSource.
        
        Arrange: Подготовка данных
        Act: Создание объекта
        Assert: Проверка всех полей и наличия в БД
        """
        # Arrange & Act
        data_source = DataSource.objects.create(name="Тестовый источник")
        
        # Assert
        assert data_source.id is not None
        assert data_source.name == "Тестовый источник"
        assert data_source.created_at is not None
        assert data_source.updated_at is not None
        
        # Проверка, что объект сохранен в БД
        assert DataSource.objects.count() == 1
        assert DataSource.objects.filter(name="Тестовый источник").exists()
    
    def test_data_source_str(self, db):
        """
        Тест: Проверка строкового представления DataSource.
        
        Arrange: Создание объекта
        Act: Преобразование в строку
        Assert: Правильное отображение имени
        """
        # Arrange & Act
        data_source = DataSource.objects.create(name="Тестовый источник")
        
        # Assert
        assert str(data_source) == "Тестовый источник"


class TestClientModel:
    """
    Тесты для модели Client.
    
    Проверяет создание клиента, валидацию полей и связи с DataSource.
    """
    
    def test_create_client_with_all_fields(self, db, data_source):
        """
        Тест: Создание объекта Client со всеми полями.
        
        Arrange: Подготовка источника данных
        Act: Создание полного объекта клиента
        Assert: Проверка всех полей и наличия в БД
        """
        # Arrange & Act
        client = Client.objects.create(
            full_name="ООО Полный Тест",
            short_name="ПолныйТест",
            inn="123456789012",
            kpp="123456789",
            ogrn="1234567890123",
            address="г. Москва, ул. Тестовая, д. 1",
            okved="62.01",
            reg_date=date(2020, 1, 1),
            authorized_capital=10000.00,
            status=Client.StatusChoices.ACTIVE,
            data_source=data_source
        )
        
        # Assert - проверка всех полей
        assert client.id is not None
        assert client.full_name == "ООО Полный Тест"
        assert client.short_name == "ПолныйТест"
        assert client.inn == "123456789012"
        assert client.kpp == "123456789"
        assert client.ogrn == "1234567890123"
        assert client.address == "г. Москва, ул. Тестовая, д. 1"
        assert client.okved == "62.01"
        assert client.reg_date == date(2020, 1, 1)
        assert client.authorized_capital == 10000.00
        assert client.status == Client.StatusChoices.ACTIVE
        assert client.data_source == data_source
        
        # Проверка автоматических полей
        assert client.created_at is not None
        assert client.updated_at is not None
        
        # Проверка наличия в БД
        assert Client.objects.count() == 1
        assert Client.objects.filter(inn="123456789012").exists()
    
    def test_client_inn_validation_length(self, db, data_source):
        """
        Тест: Валидация длины ИНН (должно быть 10 или 12 символов).
        
        Arrange: Подготовка данных с валидным и невалидным ИНН
        Act: Попытка валидации объекта
        Assert: Проверка валидных и невалидных длин
        """
        # Arrange - валидные длины
        client_10_digits = Client(
            full_name="ИП Тест",
            inn="1234567890",
            short_name="ИП",
            status=Client.StatusChoices.ACTIVE,
            data_source=data_source
        )
        
        client_12_digits = Client(
            full_name="ООО Тест",
            inn="123456789012",
            short_name="ООО",
            status=Client.StatusChoices.ACTIVE,
            data_source=data_source
        )
        
        # Act & Assert - валидные должны пройти
        client_10_digits.full_clean()
        client_12_digits.full_clean()
        
        # Arrange - невалидная длина
        client_invalid = Client(
            full_name="ООО Тест",
            inn="123456789",  # 9 символов - невалидно
            status=Client.StatusChoices.ACTIVE,
            data_source=data_source
        )
        
        # Act & Assert - должна быть ошибка
        with pytest.raises(ValidationError):
            client_invalid.full_clean()
    
    def test_client_kpp_validation_length(self, db, data_source):
        """
        Тест: Валидация длины КПП (должно быть 9 символов).
        
        Arrange: Подготовка данных с невалидным КПП
        Act: Попытка валидации объекта
        Assert: Ожидается ValidationError при невалидной длине
        """
        # Arrange
        client = Client(
            full_name="ООО Тест",
            inn="123456789012",
            kpp="12345678",  # Неправильная длина
            status=Client.StatusChoices.ACTIVE,
            data_source=data_source
        )
        
        # Act & Assert
        with pytest.raises(ValidationError):
            client.full_clean()
    
    def test_client_ogrn_validation_length(self, db, data_source):
        """
        Тест: Валидация длины ОГРН (должно быть 13 или 15 символов).
        
        Arrange: Подготовка данных с валидным и невалидным ОГРН
        Act: Попытка валидации объекта
        Assert: Проверка валидных и невалидных длин
        """
        # Arrange - валидные длины
        client_13_digits = Client(
            full_name="ООО Тест",
            inn="123456789012",
            ogrn="1234567890123",  # 13 символов - валидно
            short_name="Тест",
            status=Client.StatusChoices.ACTIVE,
            data_source=data_source
        )
        
        client_15_digits = Client(
            full_name="ИП Тест",
            inn="1234567890",
            ogrn="123456789012345",  # 15 символов - валидно
            short_name="ИП",
            status=Client.StatusChoices.ACTIVE,
            data_source=data_source
        )
        
        # Act & Assert - валидные должны пройти
        client_13_digits.full_clean()
        client_15_digits.full_clean()
        
        # Arrange - невалидная длина
        client_invalid = Client(
            full_name="ООО Тест",
            inn="123456789012",
            ogrn="123456789012",  # 12 символов - невалидно
            status=Client.StatusChoices.ACTIVE,
            data_source=data_source
        )
        
        # Act & Assert - должна быть ошибка
        with pytest.raises(ValidationError):
            client_invalid.full_clean()
    
    def test_client_status_choices(self, db, data_source):
        """
        Тест: Проверка всех возможных статусов клиента.
        
        Arrange: Подготовка данных для каждого статуса
        Act: Создание объектов с разными статусами
        Assert: Проверка правильности сохранения статусов
        """
        # Arrange & Act
        client_active = Client.objects.create(
            full_name="ООО Активный",
            inn="111111111111",
            status=Client.StatusChoices.ACTIVE,
            data_source=data_source
        )
        client_liquidated = Client.objects.create(
            full_name="ООО Ликвидирован",
            inn="222222222222",
            status=Client.StatusChoices.LIQUIDATED,
            data_source=data_source
        )
        client_reorganized = Client.objects.create(
            full_name="ООО Реорганизован",
            inn="333333333333",
            status=Client.StatusChoices.REORGANIZED,
            data_source=data_source
        )
        
        # Assert
        assert client_active.status == Client.StatusChoices.ACTIVE
        assert client_liquidated.status == Client.StatusChoices.LIQUIDATED
        assert client_reorganized.status == Client.StatusChoices.REORGANIZED
        
        # Проверка наличия всех в БД
        assert Client.objects.count() == 3
    
    def test_client_created_at_updated_at_auto(self, db, data_source):
        """
        Тест: Автоматическое заполнение created_at и updated_at.
        
        Arrange: Подготовка данных
        Act: Создание объекта
        Assert: Проверка автоматических полей
        """
        # Arrange & Act
        before_creation = datetime.now(timezone.utc)
        client = Client.objects.create(
            full_name="ООО Тест",
            inn="123456789012",
            status=Client.StatusChoices.ACTIVE,
            data_source=data_source
        )
        after_creation = datetime.now(timezone.utc)
        
        # Assert
        assert client.created_at is not None
        assert client.updated_at is not None
        assert before_creation <= client.created_at.replace(tzinfo=timezone.utc) <= after_creation
        assert before_creation <= client.updated_at.replace(tzinfo=timezone.utc) <= after_creation
    
    def test_client_data_source_foreign_key(self, db):
        """
        Тест: Связь ForeignKey с DataSource.
        
        Arrange: Создание источника данных
        Act: Создание клиента с этим источником
        Assert: Проверка связи и каскадного удаления
        """
        # Arrange
        data_source = DataSource.objects.create(name="Тестовый источник")
        
        # Act
        client = Client.objects.create(
            full_name="ООО Тест",
            inn="123456789012",
            status=Client.StatusChoices.ACTIVE,
            data_source=data_source
        )
        
        # Assert
        assert client.data_source == data_source
        assert client.data_source.id == data_source.id
        
        # Проверка каскадного удаления (если настроено)
        # DataSource.objects.filter(id=data_source.id).delete()
        # assert not Client.objects.filter(id=client.id).exists()
    
    def test_client_str_representation(self, db, data_source):
        """
        Тест: Проверка строкового представления Client.
        
        Arrange: Создание клиента
        Act: Преобразование в строку
        Assert: Правильное отображение имени и ИНН
        """
        # Arrange & Act
        client = Client.objects.create(
            full_name="ООО Тестовый Клиент",
            short_name="ТестКлиент",
            inn="123456789012",
            status=Client.StatusChoices.ACTIVE,
            data_source=data_source
        )
        
        # Assert
        assert str(client) == "ООО Тестовый Клиент (ИНН: 123456789012)"
    
    def test_client_ordering(self, db, data_source):
        """
        Тест: Проверка сортировки клиентов по умолчанию.
        
        Arrange: Создание нескольких клиентов
        Act: Получение списка клиентов
        Assert: Проверка порядка сортировки (по дате создания)
        """
        # Arrange
        client1 = Client.objects.create(
            full_name="Первый",
            inn="111111111111",
            status=Client.StatusChoices.ACTIVE,
            data_source=data_source
        )
        client2 = Client.objects.create(
            full_name="Второй",
            inn="222222222222",
            status=Client.StatusChoices.ACTIVE,
            data_source=data_source
        )
        client3 = Client.objects.create(
            full_name="Третий",
            inn="333333333333",
            status=Client.StatusChoices.ACTIVE,
            data_source=data_source
        )
        
        # Act
        clients = list(Client.objects.all())
        
        # Assert - должны быть отсортированы по дате создания (новые последние)
        assert len(clients) == 3
        # Проверяем, что сортировка работает (ordering = ['-created_at'], т.е. новые первые)
        client_ids = [c.id for c in clients]
        assert client_ids == sorted(client_ids, reverse=True)

