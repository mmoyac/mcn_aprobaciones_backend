"""
Inicialización de la base de datos PostgreSQL
"""

import asyncio
from sqlalchemy import text
from app.db.session_postgres import get_postgres_db_sync
from app.models.documento_pdf import DocumentoPDF
from app.db.base_postgres import BasePostgreSQL

async def init_db():
    """
    Crea las tablas necesarias en PostgreSQL si no existen
    """
    try:
        # Obtener sesión síncrona
        db = get_postgres_db_sync()
        
        # Crear todas las tablas definidas en BasePostgreSQL
        BasePostgreSQL.metadata.create_all(bind=db.bind)
        
        print("✅ Tablas PostgreSQL creadas/verificadas exitosamente")
        
        # Verificar que la tabla existe
        result = db.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'documentos_pdf'"))
        table_exists = result.scalar() > 0
        
        if table_exists:
            print("✅ Tabla documentos_pdf confirmada")
        else:
            print("❌ Error: Tabla documentos_pdf no fue creada")
            
    except Exception as e:
        print(f"❌ Error inicializando PostgreSQL: {str(e)}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    # Permitir ejecutar directamente para testing
    asyncio.run(init_db())