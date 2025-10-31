"""
Сервис для работы с DaData API.

Получает данные о компаниях по ИНН из DaData API.
"""
import os
import requests
from datetime import datetime
from django.conf import settings


class DaDataService:
    """
    Сервис для работы с DaData API.
    
    Предоставляет методы для получения данных о компаниях по ИНН.
    """
    
    BASE_URL = 'https://suggestions.dadata.ru/suggestions/api/4_1/rs/findById/party'
    
    def __init__(self):
        """
        Инициализация сервиса.
        
        Загружает API ключ из настроек Django.
        """
        self.api_key = os.environ.get('DADATA_API_KEY', '')
        self.timeout = getattr(settings, 'DADATA_API_TIMEOUT', 10)
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Token {self.api_key}'
        }
    
    def get_company_data_by_inn(self, inn: str, data_source_id: int = None):
        """
        Получение данных о компании по ИНН.
        
        Args:
            inn: ИНН компании (10 или 12 цифр)
            data_source_id: ID источника данных для записи в результат
            
        Returns:
            dict: Словарь с данными компании или None при ошибке
        """
        # Проверяем наличие API ключа
        if not self.api_key:
            return None
        
        try:
            # Выполнение запроса к DaData API
            response = requests.post(
                self.BASE_URL,
                headers=self.headers,
                json={'query': inn},
                timeout=self.timeout
            )
            
            # Проверка статуса ответа
            if response.status_code != 200:
                return None
            
            # Парсинг ответа
            data = response.json()
            
            # Проверка наличия данных
            if not data.get('suggestions') or len(data['suggestions']) == 0:
                return None
            
            # Извлечение данных о компании
            company_data = data['suggestions'][0]['data']
            
            # Преобразование данных в формат нашей модели
            return self._transform_dadata_response(company_data, data_source_id)
            
        except (requests.exceptions.RequestException, Exception):
            # Логирование сетевых ошибок и всех других исключений
            return None
        except (KeyError, ValueError):
            # Логирование ошибок парсинга
            return None
    
    def _transform_dadata_response(self, data: dict, data_source_id: int = None) -> dict:
        """
        Преобразование ответа DaData в формат модели Client.
        
        Args:
            data: Данные из DaData API
            data_source_id: ID источника данных
            
        Returns:
            dict: Преобразованные данные для создания Client
        """
        # Извлечение названий компании
        name_data = data.get('name', {})
        full_name = name_data.get('full_with_opf', name_data.get('full', ''))
        short_name = name_data.get('short_with_opf', name_data.get('short', ''))
        
        # Извлечение адреса
        address_data = data.get('address', {})
        address = address_data.get('unrestricted_value', '')
        
        # Извлечение ОКВЭД
        okved_main = None
        if data.get('okved'):
            okved_main = data['okved']
        elif data.get('okved_detailed') and len(data['okved_detailed']) > 0:
            okved_main = data['okved_detailed'][0]['code']
        
        # Преобразование даты регистрации из timestamp
        reg_date = None
        state_data = data.get('state', {})
        if state_data.get('registration_date'):
            timestamp = state_data['registration_date'] / 1000  # Преобразование из миллисекунд
            reg_date = datetime.fromtimestamp(timestamp).date()
        
        # Извлечение уставного капитала
        authorized_capital = None
        capital_data = data.get('capital') or {}
        if capital_data and capital_data.get('value'):
            # Форматируем значение с двумя знаками после запятой
            authorized_capital = '{:.2f}'.format(capital_data['value'])
        
        # Определение статуса компании
        status = 'active'
        if state_data.get('status') == 'LIQUIDATED':
            status = 'liquidated'
        elif state_data.get('status') == 'LIQUIDATING':
            status = 'reorganized'
        
        return {
            'full_name': full_name,
            'short_name': short_name,
            'inn': data.get('inn', ''),
            'kpp': data.get('kpp'),
            'ogrn': data.get('ogrn'),
            'address': address if address else None,
            'okved': okved_main,
            'reg_date': reg_date.isoformat() if reg_date else None,
            'authorized_capital': authorized_capital,
            'status': status,
            'data_source': data_source_id
        }

