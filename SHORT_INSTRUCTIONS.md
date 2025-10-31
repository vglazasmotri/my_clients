# Короткие инструкции по запуску

## Первый запуск

1. Создайте файл `.env` в корне проекта со следующим содержимым:

```
POSTGRES_DB=tdd_db
POSTGRES_USER=tdd_user
POSTGRES_PASSWORD=tdd_password
SECRET_KEY=django-insecure-dev-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
DB_NAME=tdd_db
DB_USER=tdd_user
DB_PASSWORD=tdd_password
DB_HOST=db
DB_PORT=5432
DADATA_API_KEY=
DADATA_API_TIMEOUT=10
```

2. Запустите Docker контейнеры:

```bash
docker-compose up --build
```

3. В новом терминале примените миграции:

```bash
docker-compose exec backend python manage.py migrate
```

4. Запустите тесты:

```bash
docker-compose exec backend pytest
```

5. Откройте в браузере:

- API: http://localhost/api/clients/
- Admin: http://localhost/admin/

## Создание суперпользователя для админки

```bash
docker-compose exec backend python manage.py createsuperuser
```

## Остановка

```bash
docker-compose down
```

## Очистка (удаление базы данных)

```bash
docker-compose down -v
```

