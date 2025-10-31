"""
Сериализаторы для приложения clients.

Преобразуют данные моделей в JSON формат и обратно.
"""
from rest_framework import serializers
from clients.models import Client, DataSource
from clients.services.dadata_service import DaDataService


class DataSourceSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели DataSource.
    
    Преобразует источники данных в JSON формат для API.
    Все поля сериализуются.
    """
    
    class Meta:
        model = DataSource
        fields = ['id', 'name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ClientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Client.
    
    Преобразует данные клиента в JSON формат и обратно.
    Включает валидацию ИНН, КПП и ОГРН по длине.
    """
    
    # Поле для отображения имени источника данных
    data_source_name = serializers.CharField(
        source='data_source.name',
        read_only=True
    )
    
    class Meta:
        model = Client
        fields = [
            'id',
            'full_name',
            'short_name',
            'inn',
            'kpp',
            'ogrn',
            'address',
            'okved',
            'reg_date',
            'authorized_capital',
            'status',
            'data_source',
            'data_source_name',
            'last_checked_at',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'data_source_name']
        extra_kwargs = {
            'full_name': {'required': False},
            'short_name': {'required': False},
            'inn': {'required': False},
        }
    
    def validate_inn(self, value):
        """
        Валидация поля ИНН.
        
        Проверяет, что ИНН состоит из 10 или 12 цифр (если указано).
        Args:
            value: Значение ИНН из запроса (может быть None)
        Returns:
            str: Валидный ИНН или None
        Raises:
            serializers.ValidationError: Если ИНН невалиден
        """
        if value is None:
            return value
        
        if not value.isdigit():
            raise serializers.ValidationError('ИНН должен содержать только цифры.')
        
        if len(value) not in (10, 12):
            raise serializers.ValidationError('ИНН должен состоять из 10 или 12 цифр.')
        
        return value
    
    def validate_kpp(self, value):
        """
        Валидация поля КПП.
        
        Проверяет, что КПП состоит из 9 цифр (если указано).
        Args:
            value: Значение КПП из запроса (может быть None)
        Returns:
            str: Валидный КПП или None
        Raises:
            serializers.ValidationError: Если КПП невалиден
        """
        if value is None:
            return value
        
        if len(value) != 9:
            raise serializers.ValidationError('КПП должен состоять из 9 цифр.')
        
        if not value.isdigit():
            raise serializers.ValidationError('КПП должен содержать только цифры.')
        
        return value
    
    def validate_ogrn(self, value):
        """
        Валидация поля ОГРН.
        
        Проверяет, что ОГРН состоит из 13 или 15 цифр (если указано).
        Args:
            value: Значение ОГРН из запроса (может быть None)
        Returns:
            str: Валидный ОГРН или None
        Raises:
            serializers.ValidationError: Если ОГРН невалиден
        """
        if value is None:
            return value
        
        if not value.isdigit():
            raise serializers.ValidationError('ОГРН должен содержать только цифры.')
        
        if len(value) not in (13, 15):
            raise serializers.ValidationError('ОГРН должен состоять из 13 или 15 цифр.')
        
        return value
    
    def validate(self, data):
        """
        Валидация всего объекта.
        
        Проверяет возможность автозаполнения данных из DaData API,
        если предоставлен только ИНН и источник данных - DaData.
        
        Args:
            data: Все данные сериализатора
            
        Returns:
            dict: Валидированные данные, возможно дополненные из DaData
        """
        # Проверяем, нужно ли автоматическое заполнение из DaData
        inn = data.get('inn')
        data_source = data.get('data_source')
        
        # Получаем ID источника данных (может быть объект или ID)
        data_source_id = None
        if isinstance(data_source, DataSource):
            data_source_id = data_source.id
            data_source_obj = data_source
        elif data_source:
            data_source_id = int(data_source) if isinstance(data_source, str) else data_source
            try:
                data_source_obj = DataSource.objects.get(id=data_source_id)
            except DataSource.DoesNotExist:
                data_source_obj = None
        else:
            data_source_obj = None
        
        # Если передан ИНН и источник данных, пытаемся получить данные из DaData
        if inn and data_source_obj and data_source_obj.name.lower() == 'dadata':
            # Получаем данные из DaData API
            dadata_service = DaDataService()
            dadata_data = dadata_service.get_company_data_by_inn(inn, data_source_id)
            
            if dadata_data:
                # Автозаполнение полей из DaData
                # Перезаписываем только те поля, которые не переданы явно
                for field in ['full_name', 'short_name', 'kpp', 'ogrn', 'address', 
                             'okved', 'reg_date', 'authorized_capital', 'status']:
                    if field not in data or not data.get(field):
                        if dadata_data.get(field):
                            data[field] = dadata_data[field]
                
                # Обновляем last_checked_at
                from django.utils import timezone
                data['last_checked_at'] = timezone.now()
        
        # Проверяем, что заполнено хотя бы одно из полей: inn или ogrn
        inn = data.get('inn')
        ogrn = data.get('ogrn')
        
        # Если это частичное обновление (PATCH), учитываем значения из instance
        # Если это полное обновление (PUT) или создание, не подставляем значения из instance
        if self.instance and getattr(self, 'partial', False):
            instance_inn = getattr(self.instance, 'inn', None)
            instance_ogrn = getattr(self.instance, 'ogrn', None)
            # Если inn не передан в запросе, берем из instance
            if inn is None:
                inn = instance_inn
            # Если ogrn не передан в запросе, берем из instance
            if ogrn is None:
                ogrn = instance_ogrn
        
        # Проверяем наличие хотя бы одного поля
        if not inn and not ogrn:
            raise serializers.ValidationError({
                'inn': 'Необходимо заполнить хотя бы одно из полей: ИНН или ОГРН.',
                'ogrn': 'Необходимо заполнить хотя бы одно из полей: ИНН или ОГРН.'
            })
        
        return data

