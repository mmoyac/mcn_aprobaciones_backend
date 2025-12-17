#!/usr/bin/env python3
"""
Script de migración automática para PostgreSQL
Crea las tablas necesarias para documentos PDF
"""

import asyncio
import asyncpg
import os
import sys
from pathlib import Path

# Configuración de conexión
POSTGRES_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'user': os.getenv('POSTGRES_USER', 'lexasdulce'),
    'password': os.getenv('POSTGRES_PASSWORD', 'Lexas1234'),
    'database': os.getenv('POSTGRES_DB', 'lexascl_gontec')
}

# SQL para crear tablas (coincide con modelo Python documentos_pdf)
CREATE_DOCUMENTOS_TABLE = """
CREATE TABLE IF NOT EXISTS documentos_pdf (
    id SERIAL PRIMARY KEY,
    numero INTEGER NOT NULL,
    tipo INTEGER NOT NULL,
    pdf BYTEA NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(numero, tipo)
);
"""

CREATE_INDEXES = """
CREATE INDEX IF NOT EXISTS idx_documentos_pdf_numero_tipo ON documentos_pdf(numero, tipo);
CREATE INDEX IF NOT EXISTS idx_documentos_pdf_tipo ON documentos_pdf(tipo);
CREATE INDEX IF NOT EXISTS idx_documentos_pdf_fecha ON documentos_pdf(fecha_creacion);
"""

async def create_tables():
    """Crear tablas y índices en PostgreSQL"""
    try:
        print(f"🔌 Conectando a PostgreSQL en {POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']}...")
        
        conn = await asyncpg.connect(
            host=POSTGRES_CONFIG['host'],
            port=POSTGRES_CONFIG['port'],
            user=POSTGRES_CONFIG['user'],
            password=POSTGRES_CONFIG['password'],
            database=POSTGRES_CONFIG['database']
        )
        
        print("✅ Conexión establecida")
        
        # Crear tabla documentos_pdf
        print("📋 Creando tabla 'documentos_pdf'...")
        await conn.execute(CREATE_DOCUMENTOS_TABLE)
        print("✅ Tabla 'documentos_pdf' creada")
        
        # Crear índices
        print("🔍 Creando índices...")
        await conn.execute(CREATE_INDEXES)
        print("✅ Índices creados")
        
        # Verificar tabla creada
        result = await conn.fetchval(
            "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'documentos_pdf'"
        )
        
        if result > 0:
            print("✅ Migración completada exitosamente")
            
            # Mostrar estadísticas
            count = await conn.fetchval("SELECT COUNT(*) FROM documentos_pdf")
            print(f"📊 Documentos PDF existentes: {count}")
            
        else:
            print("❌ Error: Tabla 'documentos_pdf' no fue creada")
            sys.exit(1)
            
        await conn.close()
        
    except Exception as e:
        print(f"❌ Error en migración: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 Iniciando migración automática PostgreSQL...")
    asyncio.run(create_tables())
    print("🎉 Migración completada")