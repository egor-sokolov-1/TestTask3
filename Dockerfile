FROM python:3.12-slim

WORKDIR /code/app

RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

COPY ../requirements.txt /code/
RUN pip install --upgrade pip && pip install --no-cache-dir -r /code/requirements.txt

COPY .. /code/

RUN adduser --disabled-password --gecos '' appuser && chown -R appuser:appuser /code
USER appuser

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
