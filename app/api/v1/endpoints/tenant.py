"""
Endpoint de configuración de tenant.
Retorna la paleta de colores y datos del tenant según el dominio (header Host).
No requiere autenticación - es el primer llamado del frontend al cargar la app.
"""
from fastapi import APIRouter, Request, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import text, inspect as sa_inspect

from app.core.deps import get_tenant_db

# Modelos de negocio (sus tablas viven en la BD MySQL del tenant / ERP del cliente).
# Se importan explícitamente para garantizar que estén registrados en el mapper
# cuando se deriva el schema requerido en /db-check (ver SPEC-001).
from app.models.orden_compra import OrdenCompra
from app.models.presupuesto import Presupuesto
from app.models.cliente import Cliente
from app.models.proveedor import Proveedor
from app.models.local import Local
from app.models.usuario import Usuario

router = APIRouter()


class TenantTemaResponse(BaseModel):
    color_primary: str
    color_secondary: str
    color_background: str
    color_surface: str
    color_text: str


class TenantConfigResponse(BaseModel):
    slug: str
    nombre: str
    dominio: str
    logo_url: Optional[str]
    tema: TenantTemaResponse


@router.get(
    "/config",
    response_model=TenantConfigResponse,
    summary="Configuración del tenant",
    description="""
    Retorna la configuración visual (paleta de colores) y datos del tenant
    identificado por el header **Host** del request.

    - En **desarrollo**: configurar el archivo hosts del sistema para que
      el dominio apunte a `127.0.0.1` (ej: `empresa1.localhost`).
    - En **producción**: el DNS del dominio apunta al VPS.

    No requiere autenticación JWT.
    """,
    tags=["Tenant"]
)
def get_tenant_config(request: Request) -> TenantConfigResponse:
    tenant = getattr(request.state, "tenant", None)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant no encontrado para este dominio"
        )

    return TenantConfigResponse(
        slug=tenant.slug,
        nombre=tenant.nombre,
        dominio=tenant.dominio,
        logo_url=tenant.logo_url,
        tema=TenantTemaResponse(
            color_primary=tenant.tema.color_primary,
            color_secondary=tenant.tema.color_secondary,
            color_background=tenant.tema.color_background,
            color_surface=tenant.tema.color_surface,
            color_text=tenant.tema.color_text,
        )
    )


# ---------------------------------------------------------------------------
# Schema esperado por la app (tabla → columnas requeridas)
# ---------------------------------------------------------------------------
# Ver SPEC-001 (docs/specs/SPEC-001-deteccion-incompatibilidad-bd.md).
#
# Las columnas requeridas se derivan de DOS fuentes para reflejar exactamente
# lo que la app realmente consulta:
#   1) BUSINESS_MODELS  → todas las columnas mapeadas por el ORM (el ORM hace
#      SELECT de todas ellas; cualquiera ausente rompe la query).
#   2) RAW_SQL_SCHEMA    → tablas que la app consulta con SQL crudo (sin modelo
#      ORM), por lo que no aparecen vía mapper.

# Modelos cuyas tablas viven en la BD MySQL del tenant (ERP del cliente).
BUSINESS_MODELS = [OrdenCompra, Presupuesto, Cliente, Proveedor, Local, Usuario]

# Tablas consultadas con SQL crudo (sin modelo ORM). Las columnas se derivan de
# las queries de los services; actualizar si cambia el SQL referenciado.
RAW_SQL_SCHEMA = {
    # ítems de orden de compra — OrdenCompraService.obtener_items (adq005 ⨝ COT012)
    "adq005": ["Loc_cod", "ocp_nro", "ocp_lin", "ocp_mat", "Ocp_Odt",
               "Ocp_De1", "Ocp_De2", "Ocp_De3", "Ocp_est", "Ocp_can", "Ocp_pre"],
    "COT012": ["mat_cod", "mat_des"],
    # detalle de presupuestos
    "cot005":  ["loc_cod", "pre_nro", "pre_lin", "pre_des", "pre_de1", "pre_de2",
                "pre_de3", "pre_de4", "pre_cpr", "pre_pre", "pre_dct"],
    "cot005l": ["loc_cod", "pre_nro", "pre_lin", "pre_dtlin", "Pre_DtTip",
                "Pre_DtCant", "Pre_DtPre", "Pre_DtDescrip"],
}


def build_required_schema() -> dict:
    """
    Construye {tabla: [columnas requeridas]} combinando las columnas mapeadas por
    cada modelo de negocio (ORM) con las tablas de SQL crudo. Ver SPEC-001.
    """
    schema: dict = {}
    for model in BUSINESS_MODELS:
        mapper = sa_inspect(model)
        schema[mapper.local_table.name] = [col.name for col in mapper.columns]
    # Las tablas de SQL crudo no deberían colisionar con las del ORM; si lo hicieran,
    # gana el ORM (más completo) y se ignora la entrada cruda.
    for tabla, columnas in RAW_SQL_SCHEMA.items():
        schema.setdefault(tabla, columnas)
    return schema


class TableCheck(BaseModel):
    tabla: str
    existe: bool
    columnas_faltantes: List[str]
    columnas_extra: List[str]
    ok: bool


class DbCheckResponse(BaseModel):
    tenant: str
    base_de_datos: str
    checks: List[TableCheck]
    tiene_errores: bool


@router.get(
    "/db-check",
    response_model=DbCheckResponse,
    summary="Diagnóstico de compatibilidad de BD del tenant",
    tags=["Tenant"]
)
def check_tenant_db(request: Request, db: Session = Depends(get_tenant_db)) -> DbCheckResponse:
    tenant = getattr(request.state, "tenant", None)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant no encontrado")

    db_name = tenant.conexion.db_name
    checks: List[TableCheck] = []

    required_schema = build_required_schema()

    # Traer TODAS las columnas de la BD en una sola consulta (1 viaje a la red en
    # vez de N `DESCRIBE`). Contra un MySQL remoto cada round-trip cuesta ~40 ms,
    # así que esto baja el endpoint de ~0.5-1 s a ~0.2 s. Ver SPEC-001.
    columnas_por_tabla: dict = {}
    for tname, cname in db.execute(text(
        "SELECT TABLE_NAME, COLUMN_NAME FROM information_schema.COLUMNS "
        "WHERE TABLE_SCHEMA = DATABASE()"
    )).fetchall():
        columnas_por_tabla.setdefault(tname.lower(), set()).add(cname.lower())

    for tabla, columnas_requeridas in required_schema.items():
        columnas_reales = columnas_por_tabla.get(tabla.lower())

        # Si la tabla no aparece en information_schema, no existe en la BD.
        if columnas_reales is None:
            checks.append(TableCheck(
                tabla=tabla,
                existe=False,
                columnas_faltantes=columnas_requeridas,
                columnas_extra=[],
                ok=False,
            ))
            continue

        faltantes = [c for c in columnas_requeridas if c.lower() not in columnas_reales]
        ok = len(faltantes) == 0

        checks.append(TableCheck(
            tabla=tabla,
            existe=True,
            columnas_faltantes=faltantes,
            columnas_extra=[],
            ok=ok,
        ))

    tiene_errores = any(not c.ok for c in checks)

    return DbCheckResponse(
        tenant=tenant.nombre,
        base_de_datos=db_name,
        checks=checks,
        tiene_errores=tiene_errores,
    )
