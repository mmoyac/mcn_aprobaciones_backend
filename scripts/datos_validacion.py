"""
Genera hojas de validación de presupuestos por tenant (SOLO LECTURA).

Consulta directamente la BD MySQL de cada tenant activo y produce, en Markdown,
los datos que el usuario debe ver en la app: indicador de pendientes,
pendientes por sucursal, los 5 pendientes más recientes, aprobados hoy por
usuario y el detalle (aprobaciones + ítems) de un presupuesto.

Se ejecuta dentro del contenedor del backend, que ya tiene acceso a PostgreSQL
(credenciales de tenants) y a los MySQL de los clientes:

    docker exec -i mcn_backend python - < scripts/datos_validacion.py > hojas.md

Ver openspec/changes/soportar-pre-nro-alfanumerico (tareas 1.1 y 6.1).
"""
from datetime import date, datetime
from urllib.parse import quote_plus

# Todas las consultas del script. Deben ser SELECT: lo verifica
# tests/test_datos_validacion.py y también _solo_lectura() en tiempo de ejecución.
SQL_PENDIENTES_TOTAL = """
    SELECT COUNT(pre_nro) FROM cot013
    WHERE Pre_vbLib = 1 AND pre_vbgg = 0 AND pre_est <> 'N'
"""

SQL_PENDIENTES_POR_SUCURSAL = """
    SELECT c.Loc_cod, l.Loc_des, COUNT(*)
    FROM cot013 c
    LEFT JOIN loc001 l ON l.Loc_cod = c.Loc_cod
    WHERE c.Pre_vbLib = 1 AND c.pre_vbgg = 0 AND c.pre_est <> 'N'
    GROUP BY c.Loc_cod, l.Loc_des
    ORDER BY c.Loc_cod
"""

SQL_PENDIENTES_RECIENTES = """
    SELECT c.Loc_cod, c.pre_nro, c.pre_fec, c.pre_rut, cl.Cli_Name, c.Pre_Neto
    FROM cot013 c
    LEFT JOIN clientea cl ON cl.Cli_Code = c.pre_rut
    WHERE c.Pre_vbLib = 1 AND c.pre_vbgg = 0 AND c.pre_est <> 'N'
    ORDER BY c.pre_fec DESC, c.Loc_cod, c.pre_nro
    LIMIT 5
"""

SQL_APROBADOS_HOY = """
    SELECT pre_vbggUsu, COUNT(*)
    FROM cot013
    WHERE pre_vbgg = 1 AND pre_vbggDt = :hoy
    GROUP BY pre_vbggUsu
    ORDER BY pre_vbggUsu
"""

SQL_DETALLE_APROBACIONES = """
    SELECT Pre_VbLibUsu, Pre_VBLibDt, pre_VbUsu, pre_VbFec, pre_vbggUsu, pre_vbggDt
    FROM cot013
    WHERE Loc_cod = :loc_cod AND pre_nro = :pre_nro
"""

SQL_DETALLE_ITEMS = """
    SELECT pre_lin, pre_des, pre_pre
    FROM cot005
    WHERE loc_cod = :loc_cod AND pre_nro = :pre_nro
    ORDER BY pre_lin
"""

TODAS_LAS_CONSULTAS = [
    SQL_PENDIENTES_TOTAL,
    SQL_PENDIENTES_POR_SUCURSAL,
    SQL_PENDIENTES_RECIENTES,
    SQL_APROBADOS_HOY,
    SQL_DETALLE_APROBACIONES,
    SQL_DETALLE_ITEMS,
]


def _solo_lectura(sql: str) -> str:
    if not sql.strip().upper().startswith("SELECT"):
        raise RuntimeError(f"Consulta no permitida (solo SELECT): {sql[:60]}")
    return sql


def _hoy_chile() -> date:
    try:
        from zoneinfo import ZoneInfo

        return datetime.now(ZoneInfo("America/Santiago")).date()
    except Exception:
        return date.today()


def _txt(v) -> str:
    if v is None:
        return "—"
    if isinstance(v, str):
        return v.strip() or "—"
    return str(v)


def _fecha(v) -> str:
    if not v or (isinstance(v, date) and v.year < 1900):
        return "—"
    return v.strftime("%d-%m-%Y")


def _monto(v) -> str:
    return "$" + f"{int(v or 0):,}".replace(",", ".")


def hoja_tenant(cn, text, slug: str, dominio: str, hoy: date) -> str:
    def q(sql, **params):
        return cn.execute(text(_solo_lectura(sql)), params).fetchall()

    out = [f"## {slug} — https://{dominio}/", ""]

    total = q(SQL_PENDIENTES_TOTAL)[0][0]
    out += [f"**Tablero → Presupuestos → Pendientes:** {total}", ""]

    por_suc = q(SQL_PENDIENTES_POR_SUCURSAL)
    if por_suc:
        out += ["| Sucursal | Pendientes |", "| :--- | ---: |"]
        out += [f"| {r[0]} · {_txt(r[1])} | {r[2]} |" for r in por_suc]
        out.append("")

    recientes = q(SQL_PENDIENTES_RECIENTES)
    if recientes:
        out += [
            "**5 pendientes más recientes** (búscalos con el filtro “N° presupuesto”):",
            "",
            "| Sucursal | N° presupuesto | Fecha | Cliente | Neto |",
            "| :--- | :--- | :--- | :--- | ---: |",
        ]
        out += [
            f"| {r[0]} | `{_txt(r[1])}` | {_fecha(r[2])} | {_txt(r[4])} | {_monto(r[5])} |"
            for r in recientes
        ]
        out.append("")

    aprobados = q(SQL_APROBADOS_HOY, hoy=hoy)
    if aprobados:
        detalle = ", ".join(f"{_txt(r[0])}: {r[1]}" for r in aprobados)
        out += [f"**Aprobados hoy ({_fecha(hoy)}) por usuario:** {detalle}", ""]
    else:
        out += [f"**Aprobados hoy ({_fecha(hoy)}):** 0 para todos los usuarios", ""]

    if recientes:
        loc_cod, pre_nro = recientes[0][0], recientes[0][1]
        out += [f"**Detalle del presupuesto `{_txt(pre_nro)}` (sucursal {loc_cod}):**", ""]
        ap = q(SQL_DETALLE_APROBACIONES, loc_cod=loc_cod, pre_nro=pre_nro)
        if ap:
            a = ap[0]
            out += [
                f"- Liberación: {_txt(a[0])} · {_fecha(a[1])}",
                f"- VB Gerente Operaciones: {_txt(a[2])} · {_fecha(a[3])}",
                f"- VB Gerencia: {_txt(a[4])} · {_fecha(a[5])}",
            ]
        items = q(SQL_DETALLE_ITEMS, loc_cod=loc_cod, pre_nro=pre_nro)
        out.append(f"- Ítems: {len(items)}")
        out += [f"  - Línea {r[0]}: {_txt(r[1])} — {_monto(r[2])}" for r in items[:5]]
        if len(items) > 5:
            out.append(f"  - … y {len(items) - 5} más")
        out.append("")

    return "\n".join(out)


def main() -> None:
    from sqlalchemy import create_engine, text

    from app.db.session_postgres import SessionPostgres
    from app.models.tenant import Tenant

    hoy = _hoy_chile()
    print(f"# Hojas de validación de presupuestos — generadas {datetime.now():%d-%m-%Y %H:%M}\n")

    pg = SessionPostgres()
    try:
        tenants = pg.query(Tenant).filter(Tenant.activo == True).order_by(Tenant.id).all()  # noqa: E712
        for t in tenants:
            c = t.conexion
            if not c:
                print(f"## {t.slug}\n\nSin conexión configurada.\n")
                continue
            url = (
                f"mysql+pymysql://{c.db_user}:{quote_plus(c.db_password)}"
                f"@{c.db_host}:{c.db_port}/{c.db_name}"
            )
            engine = create_engine(url, connect_args={"connect_timeout": 10})
            try:
                with engine.connect() as cn:
                    print(hoja_tenant(cn, text, t.slug, t.dominio, hoy))
            except Exception as e:
                motivo = getattr(e, "orig", e)
                print(
                    f"## {t.slug} — https://{t.dominio}/\n\n"
                    f"**Presupuestos no operativo en esta BD** (la app tampoco puede "
                    f"mostrarlos hoy): {motivo}\n"
                )
            finally:
                engine.dispose()
    finally:
        pg.close()


if __name__ == "__main__":
    main()
