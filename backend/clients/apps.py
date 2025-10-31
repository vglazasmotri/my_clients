from django.apps import AppConfig


class ClientsConfig(AppConfig):
    """
    Конфигурация приложения clients.
    
    Настройки для управления клиентами в системе.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'clients'
    verbose_name = 'Клиенты'

