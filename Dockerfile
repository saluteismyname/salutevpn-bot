FROM python:3.11-slim

WORKDIR /app

# Системные пакеты для сборки
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt .

# Устанавливаем зависимости с кэшированием (скачивается один раз!)
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]