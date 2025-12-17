"""
Sesión de base de datos para PostgreSQL (documentos_pdf)
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import os

POSTGRES_USER = os.getenv("POSTGRES_USER", "lexasdulce")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "Lexas1234")
POSTGRES_DB = os.getenv("POSTGRES_DB", "lexascl_gontec")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

POSTGRES_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine_postgres = create_engine(
    POSTGRES_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)

SessionPostgres = sessionmaker(autocommit=False, autoflush=False, bind=engine_postgres)


def get_postgres_db() -> Generator[Session, None, None]:
    db = SessionPostgres()
    try:
        yield db
    finally:
        db.close()


def get_postgres_db_sync() -> Session:
    """
    Función sincrónica para obtener sesión de PostgreSQL.
    Usar solo para servicios internos - recordar cerrar la sesión.
    """
    return SessionPostgres()
