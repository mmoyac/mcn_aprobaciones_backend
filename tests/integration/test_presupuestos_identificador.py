"""
Tests de integración de la spec presupuestos/identificador-presupuesto
(openspec/changes/soportar-pre-nro-alfanumerico).

Cada test corre en los dos tenants de prueba: 'numerico' (pre_nro BIGINT,
como gontec/mga/mgacom) y 'alfanumerico' (pre_nro CHAR(12), como mcn).
"""
import pytest
from sqlalchemy import text

from tests.integration import seed

pytestmark = pytest.mark.integration


def _tipo(tenant):
    return int if tenant.nombre == "numerico" else str


def _pendientes_esperados(tenant):
    return [p["pre_nro"] for p in tenant.datos["cot013"] if p["Pre_vbLib"] == 1 and p["pre_vbgg"] == 0 and p["pre_est"] != "N"]


def _fila(engine, nro):
    with engine.connect() as cn:
        return cn.execute(
            text("SELECT pre_est, pre_vbgg, pre_vbggUsu FROM cot013 WHERE Loc_cod = 1 AND pre_nro = :n"),
            {"n": nro},
        ).fetchone()


def _pdfs(engines):
    with engines["reppdf"].connect() as cn:
        return sorted(tuple(r) for r in cn.execute(text("SELECT PdfEmpCd, PdfLocCod, PdfTipo, PdfNumero FROM pdf001")))


# --- Datos semilla ------------------------------------------------------------

def test_semilla_cargada(tenant, engines):
    with engines[tenant.nombre].connect() as cn:
        for tabla in ("cot013", "cot005", "cot005l", "clientea", "loc001", "ctbm01"):
            n = cn.execute(text(f"SELECT COUNT(*) FROM `{tabla}`")).scalar()
            assert n == len(tenant.datos[tabla]), tabla
    assert len(_pdfs(engines)) == len(seed.PDFS)


# --- Lectura ------------------------------------------------------------------

def test_pendientes_coinciden_con_indicador(api, tenant):
    indicador = api.get("/presupuestos/indicadores").json()["pendientes"]
    r = api.get("/presupuestos/pendientes")
    assert r.status_code == 200, r.text
    nros = [p["pre_nro"] for p in r.json()]
    assert len(nros) == indicador == len(_pendientes_esperados(tenant))
    assert sorted(map(str, nros)) == sorted(map(str, _pendientes_esperados(tenant)))
    assert all(isinstance(n, _tipo(tenant)) for n in nros)


def test_pendientes_conservan_formato_exacto(api, tenant):
    if tenant.nombre != "alfanumerico":
        pytest.skip("solo aplica a pre_nro alfanumérico")
    nros = [p["pre_nro"] for p in api.get("/presupuestos/pendientes").json()]
    assert "00123-2026-0" in nros  # ceros a la izquierda y guiones intactos


def test_aprobados_hoy(api, tenant):
    hoy = seed.hoy_chile().isoformat()
    r = api.get("/presupuestos/aprobados", params={"usuario": seed.USUARIO, "fecha_desde": hoy, "fecha_hasta": hoy})
    assert r.status_code == 200, r.text
    assert [p["pre_nro"] for p in r.json()] == [tenant.datos["nros"]["aprobado"]]


def test_historico(api, tenant):
    r = api.get("/presupuestos/historico", params={"q": "ALFA"})
    assert r.status_code == 200, r.text
    assert [p["pre_nro"] for p in r.json()] == [tenant.datos["nros"]["a"]]


def test_detalle_trae_solo_ese_presupuesto(api, tenant):
    nro = tenant.datos["nros"]["a"]
    r = api.get(f"/presupuestos/1/{nro}/detalle")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["pre_nro"] == nro
    assert [i["pre_des"] for i in body["items"]] == [f"ITEM 1 DE {nro}", f"ITEM 2 DE {nro}"]
    assert [c["Pre_DtDescrip"] for c in body["items"][0]["costos"]] == [f"COSTO DE {nro}"]
    assert body["aprobaciones"]["pre_vblibusu"] == "LIBERADOR"


def test_detalle_inexistente_no_falla(api, tenant):
    nro = "99999" if tenant.nombre == "numerico" else "99999-2026-0"
    r = api.get(f"/presupuestos/1/{nro}/detalle")
    assert r.status_code == 200, r.text
    assert r.json()["items"] == []


def test_detalle_rechaza_caracteres_invalidos(api, tenant):
    r = api.get("/presupuestos/1/1%27%20OR%201=1/detalle")
    assert r.status_code == 422


# --- Escritura ----------------------------------------------------------------

def test_aprobar_afecta_solo_ese_presupuesto(api, tenant, engines):
    a, b = tenant.datos["nros"]["a"], tenant.datos["nros"]["b"]
    r = api.post("/presupuestos/aprobar", json={"Loc_cod": 1, "pre_nro": a})
    assert r.status_code == 200, r.text
    assert r.json()["pre_nro"] == a
    assert _fila(engines[tenant.nombre], a)[1:] == (1, seed.USUARIO)
    assert _fila(engines[tenant.nombre], b)[1] == 0


def test_anular_afecta_solo_ese_presupuesto(api, tenant, engines):
    a, b = tenant.datos["nros"]["a"], tenant.datos["nros"]["b"]
    r = api.post("/presupuestos/anular", json={"Loc_cod": 1, "pre_nro": a})
    assert r.status_code == 200, r.text
    assert r.json()["pre_nro"] == a
    assert _fila(engines[tenant.nombre], a)[0] == "N"
    assert _fila(engines[tenant.nombre], b)[0] == "A"


def test_desaprobar_afecta_solo_ese_presupuesto(api, tenant, engines):
    aprobado = tenant.datos["nros"]["aprobado"]
    r = api.post("/presupuestos/desaprobar", json={"Loc_cod": 1, "pre_nro": aprobado})
    assert r.status_code == 200, r.text
    assert r.json()["pre_nro"] == aprobado
    assert _fila(engines[tenant.nombre], aprobado)[1] == 0


@pytest.mark.parametrize("accion", ["aprobar", "anular", "desaprobar"])
def test_accion_sobre_inexistente_da_404(api, tenant, engines, accion):
    nro = 99999 if tenant.nombre == "numerico" else "99999-2026-0"
    antes = [_fila(engines[tenant.nombre], n) for n in tenant.datos["nros"].values()]
    r = api.post(f"/presupuestos/{accion}", json={"Loc_cod": 1, "pre_nro": nro})
    assert r.status_code == 404, r.text
    assert [_fila(engines[tenant.nombre], n) for n in tenant.datos["nros"].values()] == antes


def test_numero_enviado_como_string_en_tenant_numerico(api, tenant, engines):
    if tenant.nombre != "numerico":
        pytest.skip("solo aplica a pre_nro numérico")
    r = api.post("/presupuestos/aprobar", json={"Loc_cod": 1, "pre_nro": "12345"})
    assert r.status_code == 200, r.text
    assert _fila(engines["numerico"], 12345)[1] == 1


# --- PDFs (REPPDF) -------------------------------------------------------------

def test_tienepdf(api, tenant):
    pdfs = {p["pre_nro"]: p["tienepdf"] for p in api.get("/presupuestos/pendientes").json()}
    if tenant.nombre == "numerico":
        assert pdfs == {6798: 1, 12345: 0}
    else:
        # '06798-2026-0' evaluado como resta daría 4772, que sí tiene PDF: no debe verse.
        assert set(pdfs.values()) == {0}


def test_aprobar_alfanumerico_no_borra_pdfs(api, tenant, engines):
    antes = _pdfs(engines)
    api.post("/presupuestos/aprobar", json={"Loc_cod": 1, "pre_nro": tenant.datos["nros"]["a"]})
    despues = _pdfs(engines)
    if tenant.nombre == "numerico":
        assert despues == [p for p in antes if p != (1, 1, 1, 6798)]
    else:
        assert despues == antes


def test_reppdf_nunca_recibe_identificadores_alfanumericos(api, tenant):
    from sqlalchemy import event
    from sqlalchemy.engine import Engine

    enviados = []

    def _capturar(conn, cursor, statement, parameters, context, executemany):
        if "pdf001" in statement:
            enviados.append((statement, repr(parameters)))

    event.listen(Engine, "before_cursor_execute", _capturar)
    try:
        api.get("/presupuestos/pendientes")
        api.get("/presupuestos/historico", params={"q": "ALFA"})
        api.post("/presupuestos/aprobar", json={"Loc_cod": 1, "pre_nro": tenant.datos["nros"]["a"]})
    finally:
        event.remove(Engine, "before_cursor_execute", _capturar)

    if tenant.nombre == "numerico":
        assert enviados, "el tenant numérico debe seguir consultando REPPDF"
    else:
        assert enviados == []
    assert not any("-2026-" in stmt or "-2026-" in params for stmt, params in enviados)
