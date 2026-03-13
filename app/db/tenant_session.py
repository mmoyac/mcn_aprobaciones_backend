"""
Sesión dinámica de MySQL por tenant.
Crea conexiones a la BD MySQL de cada tenant usando sus credenciales almacenadas en PostgreSQL.
Las engines se cachean por URL para no recrearlas en cada request.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

_engine_cache: dict = {}


def _get_or_create_engine(url: str):
    """Retorna engine existente o crea uno nuevo y lo cachea."""
    if url not in _engine_cache:
        _engine_cache[url] = create_engine(
            url,
            pool_pre_ping=True,
            pool_recycle=3600,
            pool_size=5,
            max_overflow=10,
        )
    return _engine_cache[url]


def create_tenant_session(db_host: str, db_port: int, db_name: str, db_user: str, db_password: str) -> Session:
    """
    Crea y retorna una sesión SQLAlchemy para la BD MySQL del tenant.
    Recordar cerrar la sesión después de usarla.
    """
    url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?charset=utf8mb4"
    engine = _get_or_create_engine(url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()
