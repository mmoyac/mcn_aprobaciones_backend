#!/bin/sh
set -e

echo "==> Ejecutando migraciones Alembic..."
alembic upgrade head
echo "==> Migraciones completadas."

echo "==> Iniciando servidor FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
