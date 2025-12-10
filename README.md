# Payouts API - Django + DRF + Celery + Redis + Docker

### 
- Асинхронная обработка выплат через Celery + Redis
- Полный CRUD API
- Валидация на уровне сериализаторов
- Автоматические миграции при запуске
- Полностью контейнеризировано (Docker + docker-compose)
- Тесты с мокингом Celery
- CI пайплайн с запуском тестов, линтеров, форматтеров
- Документация API

## Локальный запуск (через Docker)

- git clone https://github.com/egor-sokolov-1/TestTask3
- cd TZ3
- docker-compose up --build

API доступно по http://localhost:8000/api/payouts/ и т.д.

## Документация API

- Swagger UI: http://localhost:8000/api/swagger/
- Redoc: http://localhost:8000/api/redoc/
- OpenAPI схема: http://localhost:8000/api/schema/

# По деплою
### 1. Клонируем репозиторий, создаём venv, ставим зависимости
pip install -r requirements.txt gunicorn psycopg2-binary

### 2. Настраиваем settings.py
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']
DATABASE_URL = os.environ['DATABASE_URL']
CELERY_BROKER_URL = os.environ['REDIS_URL']

### 3. Собираем статику
python manage.py collectstatic --noinput

### 4. Применяем миграции
python manage.py migrate

### 5. Запускаем через systemd:

### gunicorn.service
ExecStart=/venv/bin/gunicorn config.wsgi:application \
  --workers 3 --bind unix:/run/gunicorn.sock

### celery.service
ExecStart=/venv/bin/celery -A config worker -l info

### celery-beat.service (по желанию)
ExecStart=/venv/bin/celery -A config beat -l info

Nginx проксирует на unix:/run/gunicorn.sock и обслуживает статику

# CI
Flake8 + Black + тесты (payouts.tests) + Сборка Docker образа
