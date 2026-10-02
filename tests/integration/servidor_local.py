"""
Levanta el backend en http://localhost:$PUERTO (8050 por defecto) contra el MySQL de pruebas
(docker-compose.test.yml), con dos tenants para probar el frontend a mano:

    http://numerico.localhost:<puerto front>      -> pre_nro BIGINT   (como gontec/mga/mgacom)
    http://alfanumerico.localhost:<puerto front>  -> pre_nro CHAR(12) (como mcn)

    docker compose -f docker-compose.test.yml up -d
    PUERTO=8060 python -m tests.integration.servidor_local
    # en el frontend: NEXT_PUBLIC_API_PORT=8060 npx next dev -p 3060

Imprime un token para el usuario TESTER: en el navegador, crear las cookies
`access_token=<token>` y `user={"usuario":"TESTER","nombre":"TESTER"}`.
"""
import os
from datetime import timedelta
from types import SimpleNamespace

os.environ["SECRET_KEY"] = "clave-de-pruebas-de-integracion"

from sqlalchemy import create_engine  # noqa: E402

from tests.integration import conftest, seed  # noqa: E402

TEMA = SimpleNamespace(
    color_primary="#4DB848", color_secondary="#45A29A", color_background="#0F172A",
    color_surface="#1E293B", color_text="#F8FAFC",
)


def main() -> None:
    import uvicorn

    import app.main as main_module
    from app.core import tenant_middleware
    from app.core.security import create_access_token

    for nombre, t in conftest.TENANTS.items():
        t.dominio = f"{nombre}.localhost"
        t.nombre = f"Pruebas {nombre}"
        t.logo_url = None
        t.tema = TEMA
        seed.cargar(create_engine(conftest._url(t.esquema)), nombre)
    seed.cargar_pdfs(create_engine(conftest._url("t_reppdf")))

    tenant_middleware.SessionPostgres = conftest._FakePostgres
    main_module.SessionPostgres = conftest._FakePostgres  # CORS dinámico
    os.environ.update({
        "REPPDF_HOST": conftest.HOST, "REPPDF_PORT": str(conftest.PORT), "REPPDF_DB": "t_reppdf",
        "REPPDF_USER": conftest.USER, "REPPDF_PASSWORD": conftest.PASSWORD,
    })
    print("TOKEN", create_access_token({"sub": seed.USUARIO}, expires_delta=timedelta(hours=8)), flush=True)

    uvicorn.run(main_module.app, host="127.0.0.1", port=int(os.getenv("PUERTO", "8050")))


if __name__ == "__main__":
    main()
