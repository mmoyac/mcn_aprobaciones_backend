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

# SQL para crear tablas
CREATE_DOCUMENTS_TABLE = """
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    loc_cod INTEGER NOT NULL,
    numero INTEGER NOT NULL,
    tipo INTEGER NOT NULL,
    filename VARCHAR(255) NOT NULL,
    content_type VARCHAR(100),
    file_data BYTEA NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Índices para búsqueda eficiente
    UNIQUE(loc_cod, numero, tipo)
);
"""

CREATE_INDEXES = """
CREATE INDEX IF NOT EXISTS idx_documents_loc_numero ON documents(loc_cod, numero);
CREATE INDEX IF NOT EXISTS idx_documents_tipo ON documents(tipo);
CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at);
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
        
        # Crear tabla documents
        print("📋 Creando tabla 'documents'...")
        await conn.execute(CREATE_DOCUMENTS_TABLE)
        print("✅ Tabla 'documents' creada")
        
        # Crear índices
        print("🔍 Creando índices...")
        await conn.execute(CREATE_INDEXES)
        print("✅ Índices creados")
        
        # Verificar tabla creada
        result = await conn.fetchval(
            "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'documents'"
        )
        
        if result > 0:
            print("✅ Migración completada exitosamente")
            
            # Mostrar estadísticas
            count = await conn.fetchval("SELECT COUNT(*) FROM documents")
            print(f"📊 Documentos existentes: {count}")
            
        else:
            print("❌ Error: Tabla 'documents' no fue creada")
            sys.exit(1)
            
        await conn.close()
        
    except Exception as e:
        print(f"❌ Error en migración: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 Iniciando migración automática PostgreSQL...")
    asyncio.run(create_tables())
    print("🎉 Migración completada")