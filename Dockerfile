FROM python:3.13-slim

# Установка зависимостей системы
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Установка зависимостей Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование проекта
COPY . .

# Создаем директории для статики и медиа
RUN mkdir -p staticfiles media

# Переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Порт для Gunicorn
EXPOSE 8000

# Команда по умолчанию (будет переопределена в docker-compose.yml)
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]