FROM python:3.12-slim AS builder

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
      libpq-dev \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

ENV PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=samevibe.settings

RUN printf '#!/bin/sh\n' \
    'set -e\n' \
    '# Ждём, пока БД станет доступной\n' \
    'until nc -z $DATABASE_HOST $DATABASE_PORT; do echo "Waiting for postgres..."; sleep 1; done\n' \
    '# Применяем миграции\n' \
    'python samevibe/manage.py migrate --noinput\n' \
    '# Собираем статику\n' \
    'python samevibe/manage.py collectstatic --noinput\n' \
    '# Запускаем Daphne\n' \
    'exec daphne -b 0.0.0.0 -p 8000 samevibe.asgi:application\n' \
  > /app/entrypoint.sh \
  && chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]