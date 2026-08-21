# Базовый образ Python 3.11 Slim
FROM python:3.11-slim

# Установка метаданных
LABEL maintainer="Pokemon RPG Team"
LABEL description="Pokemon Battle RPG (FastAPI + Oracle DB Edition)"
LABEL version="2.0.0"

# Установка рабочей директории
WORKDIR /app

# Установка системных утилит (curl для healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копирование файла зависимостей и установка библиотек Python
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Копирование исходного кода приложения
COPY backend/ /app/backend/
COPY frontend/ /app/frontend/
COPY db/ /app/db/

# Переменные окружения по умолчанию
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    SERVER_HOST=0.0.0.0 \
    SERVER_PORT=8000 \
    DB_MODE=auto

# Порт веб-приложения
EXPOSE 8000

# Healthcheck для проверки доступности FastAPI сервиса
HEALTHCHECK --interval=20s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Запуск приложения через ASGI-сервер Uvicorn
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
