#!/bin/sh
set -ex

PG_HOST="db"
PG_PORT="5432"

echo "Waiting for Postgres at ${PG_HOST}:${PG_PORT}..."
until nc -z "${PG_HOST}" "${PG_PORT}"; do
  sleep 1
done

cd /app/samevibe


echo "Start Daphne"
exec python manage.py runserver 0.0.0.0:8000