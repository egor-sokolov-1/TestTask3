.PHONY: help run migrate test worker shell lint format

help:
	@echo "Команды:"
	@echo "  make run - запуск сервера Django"
	@echo "  make migrate - применение миграций"
	@echo "  make test - запуск тестов"
	@echo "  make worker - запуск Celery worker"
	@echo "  make shell - Django shell"
	@echo "  make lint - проверка flake8"
	@echo "  make format - форматирование black"

run:
	python manage.py runserver 0.0.0.0:8000

migrate:
	python manage.py makemigrations
	python manage.py migrate

test:
	python manage.py test

worker:
	celery -A TZ3 worker -l info

shell:
	python manage.py shell

lint:
	flake8 .

format:
	black .
	