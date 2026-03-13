#!/bin/sh
set -e

echo "==> Verificando estado de migraciones Alembic..."

# Desactivar set -e temporalmente para capturar el exit code del script Python
set +e
python - <<'EOF'
import psycopg2, os, sys
try:
    conn = psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST", "postgres"),
        port=int(os.environ.get("POSTGRES_PORT", 5432)),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"]
    )
    cur = conn.cursor()
    cur.execute("SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name='alembic_version')")
    alembic_exists = cur.fetchone()[0]
    cur.execute("SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name='documentos_pdf')")
    tables_exist = cur.fetchone()[0]
    conn.close()
    if not alembic_exists and tables_exist:
        sys.exit(2)
    sys.exit(0)
except Exception as e:
    print(f"Warning al verificar DB: {e}")
    sys.exit(0)
EOF
CHECK_CODE=$?
set -e

if [ "$CHECK_CODE" -eq 2 ]; then
    echo "==> Base de datos existente sin alembic_version detectada. Stampeando con head..."
    alembic stamp head
    echo "==> Stamp completado."
fi

echo "==> Ejecutando migraciones Alembic..."
alembic upgrade head
echo "==> Migraciones completadas."

echo "==> Iniciando servidor FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000

echo "==> Ejecutando migraciones Alembic..."
alembic upgrade head
echo "==> Migraciones completadas."

echo "==> Iniciando servidor FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
