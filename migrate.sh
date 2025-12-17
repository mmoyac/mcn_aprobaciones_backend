#!/bin/bash

# =====================================
# Script de Migración - PostgreSQL
# Ejecuta migraciones automáticamente en despliegue
# =====================================

set -e  # Salir si cualquier comando falla

echo "🗃️ Iniciando migraciones de PostgreSQL..."

# Cargar variables de entorno
source .env 2>/dev/null || echo "Archivo .env no encontrado, usando valores por defecto"

# Esperar a que PostgreSQL esté disponible
echo "⏳ Esperando que PostgreSQL esté disponible..."
for i in {1..30}; do
  if docker exec mcn_postgres pg_isready -U ${POSTGRES_USER:-lexasdulce} >/dev/null 2>&1; then
    echo "✅ PostgreSQL está disponible"
    break
  fi
  echo "PostgreSQL aún no está listo - intento $i/30..."
  sleep 2
done

# Crear base de datos si no existe
echo "📊 Verificando/creando base de datos..."
docker exec mcn_postgres psql -U ${POSTGRES_USER:-lexasdulce} -c "SELECT 1 FROM pg_database WHERE datname='${POSTGRES_DB:-lexascl_gontec}';" | grep -q 1 || \
docker exec mcn_postgres psql -U ${POSTGRES_USER:-lexasdulce} -c "CREATE DATABASE ${POSTGRES_DB:-lexascl_gontec};"

# Ejecutar migraciones desde el contenedor backend
echo "🔄 Ejecutando migraciones..."
docker exec mcn_backend python -c "
import sys
sys.path.append('/app')

try:
    import asyncio
    from app.db.postgres_db import init_db
    
    async def run_migrations():
        print('📋 Inicializando tablas PostgreSQL...')
        await init_db()
        print('✅ Migraciones completadas exitosamente')
    
    asyncio.run(run_migrations())
    
except Exception as e:
    print(f'❌ Error en migraciones: {str(e)}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
"

echo "🎉 Migraciones ejecutadas exitosamente!"