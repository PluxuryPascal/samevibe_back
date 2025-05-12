FROM python:3.12-slim AS builder
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev netcat-openbsd && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python samevibe/manage.py collectstatic --noinput

FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends netcat-openbsd && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app
ENV PYTHONUNBUFFERED=1 DJANGO_SETTINGS_MODULE=samevibe.settings
RUN printf '#!/bin/sh\nset -e\nuntil nc -z $DATABASE_HOST $DATABASE_PORT; do sleep 1; done\npython samevibe/manage.py migrate --noinput\nexec python samevibe/manage.py runserver 0.0.0.0:8000\n' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh
EXPOSE 8000
ENTRYPOINT ["/app/entrypoint.sh"]