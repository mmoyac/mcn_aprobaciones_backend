"""
Endpoint de configuración de tenant.
Retorna la paleta de colores y datos del tenant según el dominio (header Host).
No requiere autenticación - es el primer llamado del frontend al cargar la app.
"""
from fastapi import APIRouter, Request, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.deps import get_tenant_db

router = APIRouter()


class TenantTemaResponse(BaseModel):
    color_primary: str
    color_secondary: str
    color_background: str
    color_surface: str
    color_text: str
    logo_url: Optional[str]


class TenantConfigResponse(BaseModel):
    slug: str
    nombre: str
    dominio: str
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
        tema=TenantTemaResponse(
            color_primary=tenant.tema.color_primary,
            color_secondary=tenant.tema.color_secondary,
            color_background=tenant.tema.color_background,
            color_surface=tenant.tema.color_surface,
            color_text=tenant.tema.color_text,
            logo_url=tenant.tema.logo_url,
        )
    )


# ---------------------------------------------------------------------------
# Schema esperado por la app (tabla → columnas requeridas)
# ---------------------------------------------------------------------------
REQUIRED_SCHEMA = {
    "cot013": [
        "Loc_cod", "pre_nro", "pre_est", "pre_gl1", "pre_fecAdj", "pre_fec",
        "pre_rut", "pre_VenCod", "Pre_Neto", "Pre_vbLib", "Pre_VbLibUsu",
        "Pre_VBLibDt", "pre_vbgg", "pre_vbggUsu", "pre_vbggDt", "pre_vbggTime",
        "pre_trnFec", "pre_trnusu",
    ],
    "clientea": ["Cli_Code", "Cli_Name"],
    "adq004": [
        "Loc_cod", "ocp_nro", "ocp_fec", "pro_rut", "ocp_net", "ocp_pdt",
        "ocp_A1_Ap", "ocp_A1_Usu", "ocp_A1_Dt", "ocp_A1_Hr",
        "ocp_A2_Ap", "ocp_A2_Usu", "ocp_A2_Dt", "ocp_A2_Hr",
    ],
    "proveea": ["pro_rut", "pro_nom"],
    "ctbm01": ["UserCd", "UserNom", "UserLlave"],
}


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

    # Obtener tablas existentes en la BD
    tablas_existentes = {
        row[0].lower()
        for row in db.execute(text("SHOW TABLES")).fetchall()
    }

    for tabla, columnas_requeridas in REQUIRED_SCHEMA.items():
        existe = tabla.lower() in tablas_existentes

        if not existe:
            checks.append(TableCheck(
                tabla=tabla,
                existe=False,
                columnas_faltantes=columnas_requeridas,
                columnas_extra=[],
                ok=False,
            ))
            continue

        # Obtener columnas reales de la tabla
        columnas_reales = {
            row[0]
            for row in db.execute(text(f"DESCRIBE `{tabla}`")).fetchall()
        }

        faltantes = [c for c in columnas_requeridas if c not in columnas_reales]
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
