# Используем официальный Python-образ
FROM python:3.12-slim

# Устанавливаем зависимости для работы с PostgreSQL и компиляции
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Указываем порт
EXPOSE 8000

# Запуск Sanic
CMD ["python", "-m", "app.main"]

