# ---- Builder ----
FROM python:3.12-slim AS builder

# 1) Установим исходники и зависимости для сборки psycopg2
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2) Скопируем зависимости и установим их
COPY   ./
RUN pip install --no-cache-dir -r requirements.txt

# 3) Скопируем весь код проекта
COPY . .

# ---- Runtime ----
FROM python:3.12-slim

# 4) Установим только runtime-зависимости для psycopg2 и netcat
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    libpq5 \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 5) Копируем установленные библиотеки и исполняемые файлы из builder’а
COPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=builder /usr/local/bin /usr/local/bin

# 6) Копируем исходники
COPY --from=builder /app /app

# 7) Переменные окружения
ENV PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=samevibe.settings

# 8) Entry-point скрипт
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]