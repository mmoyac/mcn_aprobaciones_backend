#!/bin/sh
set -e

echo "==> Verificando estado de migraciones Alembic..."

# Si la tabla alembic_version no existe pero las tablas de la app ya existen
# (base de datos creada antes de implementar alembic), stampeamos al head
# para que alembic sepa que esas migraciones ya están aplicadas.
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

if [ $? -eq 2 ]; then
    echo "==> Base de datos existente sin alembic_version detectada. Stampeando con head..."
    alembic stamp head
    echo "==> Stamp completado."
fi

echo "==> Ejecutando migraciones Alembic..."
alembic upgrade head
echo "==> Migraciones completadas."

echo "==> Iniciando servidor FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
