"""
Configuración global para pytest

IMPORTANTE: Los tests que utilizan la capa de persistencia (PostgreSQL/MySQL) 
requieren que los contenedores Docker estén ejecutándose.

Para ejecutar tests con base de datos:
1. Iniciar contenedores: docker-compose up -d
2. Ejecutar tests: pytest tests/api/test_documento_pdf.py
3. Los contenedores deben estar corriendo en localhost:5432 (PostgreSQL) y remoto para MySQL

Esta configuración permite que los tests se ejecuten desde el host local
conectándose a las bases de datos en contenedores Docker.
"""
import os
import pytest

# Configurar variables de entorno para tests ANTES de cualquier import
# NOTA: POSTGRES_HOST=localhost permite conectar desde host a contenedor Docker
os.environ["API_KEY"] = "supersecreta123"
os.environ["POSTGRES_HOST"] = "localhost" 
os.environ["POSTGRES_USER"] = "lexasdulce"
os.environ["POSTGRES_PASSWORD"] = "Lexas1234"
os.environ["POSTGRES_DB"] = "lexascl_gontec"
os.environ["POSTGRES_PORT"] = "5432"

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Configuración automática del entorno de test."""
    print("Configurando entorno de test...")
    yield
    print("Limpiando entorno de test...")