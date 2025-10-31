# REST API для управления клиентами (TDD подход)

REST API на Django REST Framework для управления информацией о юридических лицах (клиентах). Проект разработан с использованием Test-Driven Development и работает в Docker-контейнерах.

## Структура проекта

```
TDD/
├── backend/                # Django приложение
│   ├── clients/           # Основное приложение для клиентов
│   │   ├── models.py      # Модели Client и DataSource
│   │   ├── serializers.py # Сериализаторы DRF
│   │   ├── views.py       # ViewSet для API
│   │   ├── urls.py        # URL маршруты
│   │   └── tests/         # Тесты (TDD)
│   ├── config/            # Настройки Django
│   ├── Dockerfile         # Docker образ для backend
│   ├── requirements.txt   # Зависимости Python
│   └── manage.py          # Django management
├── nginx/                  # Nginx reverse proxy
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml      # Оркестрация контейнеров
└── README.md              # Документация
```

## Модель данных

### Client (Клиент)

Основная сущность - информация о юридическом лице:

- **id** - Primary Key
- **full_name** - Полное наименование
- **short_name** - Краткое наименование
- **inn** - ИНН (10 или 12 символов)
- **kpp** - КПП (9 символов)
- **ogrn** - ОГРН (13 символов)
- **address** - Юридический адрес
- **okved** - Основной ОКВЭД
- **reg_date** - Дата регистрации
- **authorized_capital** - Уставной капитал
- **status** - Статус (active, liquidated, reorganized)
- **data_source** - Связь с источником данных
- **last_checked_at** - Дата последней проверки
- **created_at**, **updated_at** - Автоматические timestamps

### DataSource (Источник данных)

Справочник источников данных для клиентов:

- **id** - Primary Key
- **name** - Название источника
- **created_at**, **updated_at** - Автоматические timestamps

**Поддерживаемые источники:**
- DaData - автоматическое заполнение данных о компании по ИНН через API DaData.ru

## Быстрый старт

### Предварительные требования

- Docker и Docker Compose
- Git

### Установка и запуск

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd TDD
```

2. Создайте файл `.env` со следующим содержимым:
```bash
# PostgreSQL настройки
POSTGRES_DB=tdd_db
POSTGRES_USER=tdd_user
POSTGRES_PASSWORD=tdd_password

# Django настройки
SECRET_KEY=django-insecure-dev-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# База данных
DB_NAME=tdd_db
DB_USER=tdd_user
DB_PASSWORD=tdd_password
DB_HOST=db
DB_PORT=5432

# DaData API (опционально)
DADATA_API_KEY=
DADATA_API_TIMEOUT=10
```

3. Запустите контейнеры:
```bash
docker-compose build
docker-compose up -d
```

4. Примените миграции базы данных:
```bash
docker-compose exec backend python manage.py migrate
```

5. Создайте суперпользователя (опционально):
```bash
docker-compose exec backend python manage.py createsuperuser
```

6. Запустите тесты:
```bash
docker-compose exec backend pytest
```

### Проверка работы

- **API:** http://localhost/api/clients/
- **Admin:** http://localhost/admin/
- **API документация:** http://localhost/api/

## Тестирование (TDD)

Проект разработан с использованием подхода Test-Driven Development:

### Структура тестов

```
clients/tests/
├── test_models.py            # Тесты моделей
├── test_serializers.py       # Тесты сериализаторов
├── test_api.py               # Тесты API эндпоинтов
└── test_dadata_integration.py # Тесты интеграции с DaData
```

### Запуск тестов

```bash
# Все тесты
docker-compose exec backend pytest

# Конкретный файл тестов
docker-compose exec backend pytest clients/tests/test_models.py

# С покрытием кода
docker-compose exec backend pytest --cov=clients

# Подробный вывод
docker-compose exec backend pytest -v
```

### Покрытие тестами

Проект имеет полное покрытие тестами:
- ✅ Создание и валидация моделей
- ✅ Сериализация и десериализация
- ✅ CRUD операции через API
- ✅ Валидация ИНН (10/12 цифр), КПП, ОГРН
- ✅ Проверка HTTP статус-кодов
- ✅ Интеграция с DaData API

## API эндпоинты

### Клиенты

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/api/clients/` | Список всех клиентов |
| POST | `/api/clients/` | Создать нового клиента |
| GET | `/api/clients/{id}/` | Получить клиента по ID |
| PUT | `/api/clients/{id}/` | Полное обновление клиента |
| PATCH | `/api/clients/{id}/` | Частичное обновление клиента |
| DELETE | `/api/clients/{id}/` | Удалить клиента |

### Пример запросов

#### Создание клиента

**Создание вручную:**
```bash
curl -X POST http://localhost/api/clients/ \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "ООО Тестовая Компания",
    "short_name": "ТестКом",
    "inn": "123456789012",
    "kpp": "123456789",
    "ogrn": "1234567890123",
    "address": "г. Москва, ул. Тестовая, д. 1",
    "okved": "62.01",
    "reg_date": "2020-01-01",
    "authorized_capital": "10000.00",
    "status": "active",
    "data_source": 1
  }'
```

**Автоматическое заполнение через DaData (только ИНН):**
```bash
curl -X POST http://localhost/api/clients/ \
  -H "Content-Type: application/json" \
  -d '{
    "inn": "7707083893",
    "data_source": 2
  }'
```
*Примечание: Для использования DaData требуется создать источник данных с названием "DaData" и указать его ID в `data_source`*

#### Получение списка клиентов

```bash
curl http://localhost/api/clients/
```

#### Получение клиента по ID

```bash
curl http://localhost/api/clients/1/
```

#### Обновление клиента

```bash
curl -X PATCH http://localhost/api/clients/1/ \
  -H "Content-Type: application/json" \
  -d '{"status": "liquidated"}'
```

#### Удаление клиента

```bash
curl -X DELETE http://localhost/api/clients/1/
```

## Разработка

### Технологии

- **Django 4.2** - веб-фреймворк
- **Django REST Framework** - API фреймворк
- **PostgreSQL** - база данных
- **pytest** - фреймворк тестирования
- **Docker** - контейнеризация
- **Nginx** - reverse proxy

### TDD Workflow

1. **Red** - Написать тест, который падает
2. **Green** - Написать минимальный код для прохождения теста
3. **Refactor** - Улучшить код, сохранив тесты зелёными

### Добавление нового функционала

1. Напишите тесты для нового функционала
2. Запустите тесты - они должны упасть (Red)
3. Реализуйте минимальный функционал
4. Проверьте, что тесты проходят (Green)
5. Отрефакторьте код при необходимости

## Остановка и очистка

```bash
# Остановка контейнеров
docker-compose down

# Остановка и удаление volumes
docker-compose down -v

# Пересборка без кеша
docker-compose build --no-cache
```

## Лицензия

MIT License

## Автор

Разработано с использованием TDD подхода

