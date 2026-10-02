"""
Fixtures de integración: API completa contra el MySQL de docker-compose.test.yml.

    docker compose -f docker-compose.test.yml up -d
    pytest -m integration

Si el MySQL de prueba no está arriba, los tests se saltan.
"""
import os
import socket
from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine

from tests.integration import seed

HOST, PORT, USER, PASSWORD = "127.0.0.1", 3356, "root", "test"

TENANTS = {
    "numerico": SimpleNamespace(id=1, slug="t-numerico", dominio="numerico.test", esquema="t_numerico"),
    "alfanumerico": SimpleNamespace(id=6, slug="t-alfanumerico", dominio="alfanumerico.test", esquema="t_alfanumerico"),
}


def _mysql_arriba() -> bool:
    try:
        socket.create_connection((HOST, PORT), 2).close()
        return True
    except OSError:
        return False


def pytest_collection_modifyitems(config, items):
    if _mysql_arriba():
        return
    skip = pytest.mark.skip(reason="MySQL de prueba no disponible (docker-compose.test.yml)")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip)


def _url(esquema: str) -> str:
    return f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{esquema}?charset=utf8mb4"


@pytest.fixture(scope="session")
def engines():
    es = {nombre: create_engine(_url(t.esquema)) for nombre, t in TENANTS.items()}
    es["reppdf"] = create_engine(_url("t_reppdf"))
    yield es
    for e in es.values():
        e.dispose()


class _FakePostgres:
    """Reemplaza SessionPostgres en el middleware: resuelve el tenant por dominio."""

    def query(self, _model):
        return self

    def filter(self, condicion_dominio, *_):
        dominio = condicion_dominio.right.value
        self._tenant = next((t for t in _tenants_con_conexion() if t.dominio == dominio), None)
        return self

    def first(self):
        return self._tenant

    def close(self):
        pass


def _tenants_con_conexion():
    for t in TENANTS.values():
        t.conexion = SimpleNamespace(
            db_host=HOST, db_port=PORT, db_name=t.esquema, db_user=USER, db_password=PASSWORD
        )
        yield t


@pytest.fixture
def client(monkeypatch):
    from fastapi.testclient import TestClient

    from app.core import tenant_middleware
    from app.main import app

    monkeypatch.setattr(tenant_middleware, "SessionPostgres", _FakePostgres)
    monkeypatch.setenv("REPPDF_HOST", HOST)
    monkeypatch.setenv("REPPDF_PORT", str(PORT))
    monkeypatch.setenv("REPPDF_DB", "t_reppdf")
    monkeypatch.setenv("REPPDF_USER", USER)
    monkeypatch.setenv("REPPDF_PASSWORD", PASSWORD)
    return TestClient(app)


@pytest.fixture
def token():
    from app.core.security import create_access_token

    return create_access_token({"sub": seed.USUARIO})


@pytest.fixture(params=["numerico", "alfanumerico"])
def tenant(request, engines):
    """Tenant de prueba con datos recién cargados (se recarga en cada test)."""
    nombre = request.param
    datos = seed.cargar(engines[nombre], nombre)
    seed.cargar_pdfs(engines["reppdf"])
    return SimpleNamespace(nombre=nombre, datos=datos, **vars(TENANTS[nombre]))


@pytest.fixture
def api(client, token, tenant):
    """Cliente HTTP ya autenticado y apuntando al tenant del test."""
    headers = {"Authorization": f"Bearer {token}", "X-Tenant-Domain": tenant.dominio}

    class _Api:
        def get(self, path, **kw):
            return client.get(f"/api/v1{path}", headers=headers, **kw)

        def post(self, path, **kw):
            return client.post(f"/api/v1{path}", headers=headers, **kw)

    return _Api()


os.environ.setdefault("SECRET_KEY", "clave-de-pruebas-de-integracion")
