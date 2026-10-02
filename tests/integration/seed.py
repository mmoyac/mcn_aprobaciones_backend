"""
Datos semilla para los tests de integración de presupuestos.

Dos tenants de prueba sobre el MySQL de docker-compose.test.yml:
  - NUMERICO     (tenant_id=1, esquema t_numerico,     pre_nro BIGINT)
  - ALFANUMERICO (tenant_id=6, esquema t_alfanumerico, pre_nro CHAR(12))

Casos límite incluidos:
  - '06798-2026-0' y '06798-2026-1': misma base, distinto sufijo (aislamiento).
  - '00123-2026-0': ceros a la izquierda.
  - PDF numérico 6798 en REPPDF para ambos tenants: aprobar '06798-2026-0' no debe borrarlo.
  - PDF 4772 del tenant 6: 06798-2026-0 evaluado como resta da 4772; no debe aparecer como PDF.
"""
from datetime import date, datetime

import pytz
from sqlalchemy import text

USUARIO = "TESTER"
FECHA = date(2026, 9, 29)


def hoy_chile() -> date:
    return datetime.now(pytz.timezone("America/Santiago")).date()


def _presupuesto(loc, nro, *, rut, neto, fec=FECHA, est="A", vblib=1, vbgg=0, vbgg_usu="", vbgg_dt=None, ref=""):
    return {
        "Loc_cod": loc,
        "pre_nro": nro,
        "pre_est": est,
        "pre_fec": fec,
        "pre_fecAdj": fec,
        "pre_rut": rut,
        "pre_suc": 0,
        "pre_VenCod": 7,
        "Pre_Neto": neto,
        "pre_gl1": f"GLOSA {nro}",
        "pre_ref": ref or f"PROYECTO {nro}",
        "Pre_vbLib": vblib,
        "Pre_VbLibUsu": "LIBERADOR",
        "Pre_VBLibDt": fec,
        "pre_vb": 0,
        "pre_VbFec": date(1000, 1, 1),
        "Pre_MailFec": date(1000, 1, 1),
        "pre_vbgg": vbgg,
        "pre_vbggUsu": vbgg_usu,
        "pre_vbggDt": vbgg_dt or date(1000, 1, 1),
        "pre_vbggTime": "",
        "pre_trnFec": fec,
        "pre_trnusu": "VENDEDOR",
    }


def datos(tenant: str) -> dict:
    hoy = hoy_chile()
    if tenant == "numerico":
        nros = {"a": 6798, "b": 12345, "aprobado": 500, "anulado": 501}
        pendientes = [
            _presupuesto(1, 6798, rut=76000001, neto=450000, ref="PROYECTO ALFA"),
            _presupuesto(1, 12345, rut=76000002, neto=1200000, fec=date(2026, 9, 28)),
        ]
        otros = []
    else:
        nros = {"a": "06798-2026-0", "b": "06798-2026-1", "c": "00123-2026-0",
                "aprobado": "06000-2026-0", "anulado": "06001-2026-0"}
        pendientes = [
            _presupuesto(1, "06798-2026-0", rut=76000001, neto=-95116, ref="PROYECTO ALFA"),
            _presupuesto(1, "06798-2026-1", rut=76000002, neto=17161375, fec=date(2026, 9, 28)),
            _presupuesto(1, "00123-2026-0", rut=76000002, neto=0, fec=date(2026, 9, 27)),
        ]
        otros = []
    otros += [
        _presupuesto(1, nros["aprobado"], rut=76000001, neto=1000, vbgg=1,
                     vbgg_usu=USUARIO, vbgg_dt=hoy),
        _presupuesto(1, nros["anulado"], rut=76000001, neto=1000, est="N"),
    ]
    a, b = nros["a"], nros["b"]
    items = [
        {"Loc_cod": 1, "pre_nro": a, "pre_lin": 1, "pre_des": f"ITEM 1 DE {a}", "pre_pre": 1000},
        {"Loc_cod": 1, "pre_nro": a, "pre_lin": 2, "pre_des": f"ITEM 2 DE {a}", "pre_pre": 2000},
        {"Loc_cod": 1, "pre_nro": b, "pre_lin": 1, "pre_des": f"ITEM 1 DE {b}", "pre_pre": 9999},
    ]
    costos = [
        {"Loc_cod": 1, "pre_nro": a, "pre_lin": 1, "Pre_DtLin": 1, "Pre_DtTip": 1,
         "Pre_DtCant": 2, "Pre_DtPre": 500, "Pre_DtDescrip": f"COSTO DE {a}"},
        {"Loc_cod": 1, "pre_nro": b, "pre_lin": 1, "Pre_DtLin": 1, "Pre_DtTip": 3,
         "Pre_DtCant": 1, "Pre_DtPre": 9999, "Pre_DtDescrip": f"COSTO DE {b}"},
    ]
    return {
        "nros": nros,
        "cot013": pendientes + otros,
        "cot005": items,
        "cot005l": costos,
        "clientea": [
            {"Cli_Code": 76000001, "Cli_Name": "CLIENTE UNO", "Cli_NameL": "CLIENTE UNO LTDA"},
            {"Cli_Code": 76000002, "Cli_Name": "CLIENTE DOS", "Cli_NameL": "CLIENTE DOS SPA"},
        ],
        "loc001": [{"Loc_cod": 1, "Loc_des": "CASA MATRIZ"}],
        "ctbm01": [{"UserCd": USUARIO, "UserDs": "USUARIO DE PRUEBA", "UserLlave": "x"}],
    }


PDFS = [
    # (PdfEmpCd, PdfLocCod, PdfTipo, PdfNumero)
    (1, 1, 1, 6798),
    (6, 1, 1, 6798),
    (6, 1, 1, 4772),
]


def _insert(cn, tabla, filas):
    for fila in filas:
        cols = ", ".join(f"`{c}`" for c in fila)
        vals = ", ".join(f":{c}" for c in fila)
        cn.execute(text(f"INSERT INTO `{tabla}` ({cols}) VALUES ({vals})"), fila)


def cargar(engine, tenant: str) -> dict:
    """Vacía y recarga el esquema del tenant. Devuelve los datos cargados."""
    d = datos(tenant)
    with engine.begin() as cn:
        for tabla in ("cot005l", "cot005", "cot013", "clientea", "loc001", "ctbm01"):
            cn.execute(text(f"DELETE FROM `{tabla}`"))
            _insert(cn, tabla, d[tabla])
    return d


def cargar_pdfs(engine) -> None:
    with engine.begin() as cn:
        cn.execute(text("DELETE FROM pdf001"))
        for emp, loc, tipo, nro in PDFS:
            cn.execute(
                text("INSERT INTO pdf001 (PdfEmpCd, PdfLocCod, PdfTipo, PdfNumero, PdfBlob) "
                     "VALUES (:e, :l, :t, :n, :b)"),
                {"e": emp, "l": loc, "t": tipo, "n": nro, "b": b"%PDF-1.4 prueba"},
            )
