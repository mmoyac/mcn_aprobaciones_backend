from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context

import sys
import os

# Añadir la raíz del proyecto al sys.path para importar app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.models import *
from app.db.base_class import Base

config = context.config
fileConfig(config.config_file_name)
target_metadata = Base.metadata


def _get_url() -> str:
    """Construye la URL de PostgreSQL desde variables de entorno si están disponibles."""
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST", "postgres")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB")
    if user and password and db:
        return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
    # Fallback a alembic.ini (desarrollo local)
    return config.get_main_option("sqlalchemy.url")


def run_migrations_offline():
    url = _get_url()
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True, compare_type=True
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = create_engine(_get_url(), poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata, compare_type=True
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
