from django.contrib import admin
from .models import DataSource, Client


@admin.register(DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    """
    Админка для модели DataSource.
    
    Управление источниками данных в интерфейсе Django Admin.
    """
    list_display = ('id', 'name', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """
    Админка для модели Client.
    
    Управление клиентами в интерфейсе Django Admin.
    """
    list_display = ('id', 'full_name', 'short_name', 'inn', 'status', 'reg_date', 'created_at')
    list_filter = ('status', 'reg_date', 'created_at')
    search_fields = ('full_name', 'short_name', 'inn', 'kpp', 'ogrn')
    readonly_fields = ('created_at', 'updated_at', 'last_checked_at')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('full_name', 'short_name', 'inn', 'kpp', 'ogrn')
        }),
        ('Адрес и регистрация', {
            'fields': ('address', 'okved', 'reg_date', 'authorized_capital')
        }),
        ('Статус и данные', {
            'fields': ('status', 'data_source', 'last_checked_at')
        }),
        ('Системные поля', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

