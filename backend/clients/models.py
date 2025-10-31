"""
Модели для приложения clients.

Определяют структуру данных для клиентов и источников данных.
"""
from django.db import models
from django.core.validators import RegexValidator


class DataSource(models.Model):
    """
    Модель источника данных.
    
    Хранит информацию об источниках, из которых получены данные о клиентах.
    """
    
    # Название источника данных
    name = models.CharField(
        max_length=255,
        verbose_name="Название источника"
    )
    
    # Автоматические поля времени создания и обновления
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )
    
    class Meta:
        verbose_name = "Источник данных"
        verbose_name_plural = "Источники данных"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class Client(models.Model):
    """
    Модель клиента.
    
    Хранит полную информацию о юридическом лице (компании).
    """
    
    # Enum для статусов клиента
    class StatusChoices(models.TextChoices):
        ACTIVE = 'active', 'Активный'
        LIQUIDATED = 'liquidated', 'Ликвидирован'
        REORGANIZED = 'reorganized', 'Реорганизован'
    
    # Валидаторы для числовых полей
    inn_validator = RegexValidator(
        regex=r'^\d{10}$|^\d{12}$',
        message='ИНН должен состоять из 10 или 12 цифр'
    )
    kpp_validator = RegexValidator(
        regex=r'^\d{9}$',
        message='КПП должен состоять из 9 цифр'
    )
    ogrn_validator = RegexValidator(
        regex=r'^\d{13}$|^\d{15}$',
        message='ОГРН должен состоять из 13 или 15 цифр'
    )
    
    # Основная информация о клиенте
    full_name = models.CharField(
        max_length=500,
        verbose_name="Полное наименование",
        blank=True,
        null=True
    )
    short_name = models.CharField(
        max_length=255,
        verbose_name="Краткое наименование",
        blank=True,
        null=True
    )
    
    # Регистрационные номера
    inn = models.CharField(
        max_length=12,
        validators=[inn_validator],
        db_index=True,
        verbose_name="ИНН",
        blank=True,
        null=True
    )
    kpp = models.CharField(
        max_length=9,
        validators=[kpp_validator],
        verbose_name="КПП",
        blank=True,
        null=True
    )
    ogrn = models.CharField(
        max_length=15,
        validators=[ogrn_validator],
        verbose_name="ОГРН",
        blank=True,
        null=True
    )
    
    # Адрес и деятельность
    address = models.TextField(
        verbose_name="Юридический адрес",
        blank=True,
        null=True
    )
    okved = models.CharField(
        max_length=100,
        verbose_name="Основной ОКВЭД",
        blank=True,
        null=True
    )
    
    # Регистрация и финансовые данные
    reg_date = models.DateField(
        verbose_name="Дата регистрации",
        blank=True,
        null=True
    )
    authorized_capital = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        verbose_name="Уставной капитал",
        blank=True,
        null=True
    )
    
    # Статус клиента
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE,
        verbose_name="Статус"
    )
    
    # Связь с источником данных
    data_source = models.ForeignKey(
        DataSource,
        on_delete=models.PROTECT,
        related_name='clients',
        verbose_name="Источник данных"
    )
    
    # Время последней проверки данных с источником
    last_checked_at = models.DateTimeField(
        verbose_name="Дата последней проверки",
        blank=True,
        null=True
    )
    
    # Автоматические поля времени создания и обновления
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )
    
    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['inn']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        name = self.full_name or self.short_name or 'Без имени'
        inn = self.inn if self.inn else 'Без ИНН'
        return f"{name} (ИНН: {inn})"
    
    def clean(self):
        """
        Валидация модели на уровне объектов.
        
        Проверяет, что заполнено хотя бы одно из полей: inn или ogrn.
        """
        from django.core.exceptions import ValidationError
        
        if not self.inn and not self.ogrn:
            raise ValidationError({
                'inn': 'Необходимо заполнить хотя бы одно из полей: ИНН или ОГРН.',
                'ogrn': 'Необходимо заполнить хотя бы одно из полей: ИНН или ОГРН.'
            })
    
    def save(self, *args, **kwargs):
        """
        Переопределение метода save для автоматической валидации.
        """
        self.full_clean()
        super().save(*args, **kwargs)

