"""
Endpoints REST API para gestión de presupuestos
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import List
import asyncio

from app.core.deps import get_tenant_db, get_current_user, get_current_user_id
from app.models.usuario import Usuario
from app.models.local import Local
from app.schemas.presupuesto import (
    PresupuestoIndicadores,
    PresupuestoDetalle,
    PresupuestoAprobar,
    PresupuestoAprobadoResponse
)
from app.schemas.presupuesto_detalle import DetallePresupuesto, PresupuestoHistorico
from app.services.presupuesto_service import PresupuestoService

router = APIRouter()


@router.get(
    "/indicadores",
    response_model=PresupuestoIndicadores,
    summary="Obtener indicadores de presupuestos",
    description="""
    Retorna los indicadores principales de presupuestos:
    
    - **Pendientes**: Presupuestos liberados pero pendientes de aprobación de gerencia
      (Pre_vbLib = 1 AND pre_vbgg = 0 y pre_est <> 'N')
    - **Aprobados**: Presupuestos aprobados por gerencia general
      (pre_vbgg = 1)
    
    Estos indicadores son útiles para dashboards y reportes ejecutivos.
    """,
    tags=["Indicadores"]
)
async def obtener_indicadores(
    db: Session = Depends(get_tenant_db),
    current_user: Usuario = Depends(get_current_user)
) -> PresupuestoIndicadores:
    """
    Obtiene los indicadores de presupuestos pendientes y aprobados.
    
    Args:
        db: Sesión de base de datos (inyectada automáticamente)
        
    Returns:
        PresupuestoIndicadores: Objeto con contadores de pendientes y aprobados
        
    Raises:
        HTTPException: Error 500 si hay problemas con la base de datos
    """
    try:
        return PresupuestoService.obtener_indicadores(db)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener indicadores: {str(e)}"
        )





@router.get(
    "/pendientes",
    response_model=List[PresupuestoDetalle],
    summary="Listar presupuestos pendientes",
    description="""
    Retorna el listado de presupuestos pendientes de aprobación.
    
    Criterio: Pre_vbLib = 1 AND pre_vbgg = 0
    
    Soporta paginación mediante parámetros skip y limit.
    """,
    tags=["Presupuestos"]
)
async def listar_presupuestos_pendientes(
    skip: int = 0,
    limit: int = 5000,
    request: Request = None,
    db: Session = Depends(get_tenant_db),
    current_user: Usuario = Depends(get_current_user)
) -> List[PresupuestoDetalle]:
    """
    Lista presupuestos pendientes de aprobación con paginación.
    
    Args:
        skip: Número de registros a omitir (default: 0)
        limit: Cantidad máxima de registros a retornar (default: 100, max: 1000)
        db: Sesión de base de datos (inyectada automáticamente)
        
    Returns:
        List[PresupuestoDetalle]: Lista de presupuestos pendientes
        
    Raises:
        HTTPException: Error 400 si los parámetros son inválidos
        HTTPException: Error 500 si hay problemas con la base de datos
    """
    if limit > 5000:
        raise HTTPException(
            status_code=400,
            detail="El límite máximo es 5000 registros"
        )

    try:
        presupuestos = PresupuestoService.obtener_presupuestos_pendientes(
            db, skip=skip, limit=limit
        )
        tenant = getattr(request.state, 'tenant', None) if request else None
        tenant_id = tenant.id if tenant else 1

        # Una sola query batch para todos los PDFs
        items = [(p.Loc_cod, p.pre_nro) for p in presupuestos]
        pdf_map = PresupuestoService._verificar_pdfs_batch(items, tenant_id, 1)

        # Batch lookup de nombres de sucursales
        loc_cods = list({p.Loc_cod for p in presupuestos})
        locales = db.query(Local).filter(Local.Loc_cod.in_(loc_cods)).all()
        loc_map = {l.Loc_cod: l.Loc_des for l in locales}

        # Enriquecer con información de PDFs y sucursal
        presupuestos_enriquecidos = []
        for presupuesto in presupuestos:
            tienepdf = pdf_map.get((presupuesto.Loc_cod, presupuesto.pre_nro), 0)

            presupuesto_dict = {
                "Loc_cod": presupuesto.Loc_cod,
                "pre_nro": presupuesto.pre_nro,
                "pre_est": presupuesto.pre_est,
                "pre_fec": presupuesto.pre_fec,
                "pre_rut": presupuesto.pre_rut,
                "cliente_nombre": presupuesto.cliente_nombre,
                "pre_VenCod": presupuesto.pre_VenCod,
                "Pre_Neto": presupuesto.Pre_Neto,
                "Pre_vbLib": presupuesto.Pre_vbLib,
                "pre_vbgg": presupuesto.pre_vbgg,
                "pre_gl1": presupuesto.pre_gl1,
                "pre_fecAdj": presupuesto.pre_fecAdj,
                "pre_VbLibUsu": presupuesto.Pre_VbLibUsu,
                "Pre_VBLibDt": presupuesto.Pre_VBLibDt,
                "pre_vbggUsu": presupuesto.pre_vbggUsu,
                "pre_vbggDt": presupuesto.pre_vbggDt,
                "pre_trnFec": presupuesto.pre_trnFec,
                "pre_trnusu": presupuesto.pre_trnusu,
                "tienepdf": tienepdf,
                "loc_des": loc_map.get(presupuesto.Loc_cod)
            }

            presupuesto_detalle = PresupuestoDetalle(**presupuesto_dict)
            presupuestos_enriquecidos.append(presupuesto_detalle)
        
        return presupuestos_enriquecidos
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener presupuestos pendientes: {str(e)}"
        )


@router.get(
    "/aprobados",
    response_model=List[PresupuestoDetalle],
    summary="Listar presupuestos aprobados por usuario y fecha",
    description="""
    Retorna el listado de presupuestos aprobados filtrados por usuario y rango de fechas.
    
    Criterios de filtro:
    - pre_vbgg = 1 (aprobado)
    - pre_vbggUsu = usuario especificado
    - pre_vbggDt entre fecha_desde y fecha_hasta
    
    Soporta paginación mediante parámetros skip y limit.
    """,
    tags=["Presupuestos"]
)
async def listar_presupuestos_aprobados(
    usuario: str,
    fecha_desde: str,
    fecha_hasta: str,
    skip: int = 0,
    limit: int = 100,
    request: Request = None,
    db: Session = Depends(get_tenant_db),
    current_user: Usuario = Depends(get_current_user)
) -> List[PresupuestoDetalle]:
    """
    Lista presupuestos aprobados filtrados por usuario y fechas.
    
    Args:
        usuario: Código del usuario que aprobó (UserCd de ctbm01)
        fecha_desde: Fecha inicial del rango (formato YYYY-MM-DD)
        fecha_hasta: Fecha final del rango (formato YYYY-MM-DD)
        skip: Número de registros a omitir (default: 0)
        limit: Cantidad máxima de registros a retornar (default: 100, max: 1000)
        db: Sesión de base de datos (inyectada automáticamente)
        
    Returns:
        List[PresupuestoDetalle]: Lista de presupuestos aprobados
        
    Raises:
        HTTPException: Error 400 si los parámetros son inválidos
        HTTPException: Error 500 si hay problemas con la base de datos
        
    Example:
        GET /api/v1/presupuestos/aprobados?usuario=admin&fecha_desde=2025-01-01&fecha_hasta=2025-12-31
    """
    if limit > 1000:
        raise HTTPException(
            status_code=400,
            detail="El límite máximo es 1000 registros"
        )
    
    try:
        presupuestos = PresupuestoService.obtener_presupuestos_aprobados(
            db, usuario=usuario, fecha_desde=fecha_desde, fecha_hasta=fecha_hasta,
            skip=skip, limit=limit
        )
        tenant = getattr(request.state, 'tenant', None) if request else None
        tenant_id = tenant.id if tenant else 1

        # Una sola query batch para todos los PDFs
        items = [(p.Loc_cod, p.pre_nro) for p in presupuestos]
        pdf_map = PresupuestoService._verificar_pdfs_batch(items, tenant_id, 1)

        # Enriquecer con información de PDFs
        presupuestos_enriquecidos = []
        for presupuesto in presupuestos:
            tienepdf = pdf_map.get((presupuesto.Loc_cod, presupuesto.pre_nro), 0)

            # Crear diccionario con todos los campos requeridos por PresupuestoDetalle
            presupuesto_dict = {
                # Campos de PresupuestoBase
                "Loc_cod": presupuesto.Loc_cod,
                "pre_nro": presupuesto.pre_nro,
                "pre_est": presupuesto.pre_est,
                "pre_fec": presupuesto.pre_fec,
                "pre_rut": presupuesto.pre_rut,
                "cliente_nombre": presupuesto.cliente_nombre,
                "pre_VenCod": presupuesto.pre_VenCod,
                "Pre_Neto": presupuesto.Pre_Neto,
                "Pre_vbLib": presupuesto.Pre_vbLib,
                "pre_vbgg": presupuesto.pre_vbgg,
                
                # Campos adicionales de PresupuestoDetalle
                "pre_gl1": presupuesto.pre_gl1,
                "pre_fecAdj": presupuesto.pre_fecAdj,
                "pre_VbLibUsu": presupuesto.Pre_VbLibUsu,
                "Pre_VBLibDt": presupuesto.Pre_VBLibDt,
                "pre_vbggUsu": presupuesto.pre_vbggUsu,
                "pre_vbggDt": presupuesto.pre_vbggDt,
                "pre_trnFec": presupuesto.pre_trnFec,
                "pre_trnusu": presupuesto.pre_trnusu,
                
                # Campo nuevo con PDF
                "tienepdf": tienepdf
            }

            # Crear objeto PresupuestoDetalle con todos los campos
            presupuesto_detalle = PresupuestoDetalle(**presupuesto_dict)
            presupuestos_enriquecidos.append(presupuesto_detalle)

        return presupuestos_enriquecidos
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener presupuestos aprobados: {str(e)}"
        )


@router.get(
    "/historico",
    response_model=List[PresupuestoHistorico],
    summary="Buscar historial de presupuestos",
    tags=["Presupuestos"]
)
async def buscar_historico(
    q: str,
    skip: int = 0,
    limit: int = 50,
    request: Request = None,
    db: Session = Depends(get_tenant_db),
    current_user: Usuario = Depends(get_current_user)
) -> List[PresupuestoHistorico]:
    try:
        tenant = getattr(request.state, 'tenant', None) if request else None
        tenant_id = tenant.id if tenant else 1
        return PresupuestoService.buscar_historico(db, q, skip=skip, limit=min(limit, 50), tenant_id=tenant_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al buscar historial: {str(e)}")


@router.get(
    "/{loc_cod}/{pre_nro}/detalle",
    response_model=DetallePresupuesto,
    summary="Obtener detalle de un presupuesto",
    tags=["Presupuestos"]
)
async def obtener_detalle_presupuesto(
    loc_cod: int,
    pre_nro: int,
    db: Session = Depends(get_tenant_db),
    current_user: Usuario = Depends(get_current_user)
) -> DetallePresupuesto:
    try:
        return PresupuestoService.obtener_detalle(db, loc_cod, pre_nro)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener detalle del presupuesto: {str(e)}"
        )


@router.post(
    "/aprobar",
    response_model=PresupuestoAprobadoResponse,
    status_code=status.HTTP_200_OK,
    summary="Aprobar presupuesto",
    description="""
    Aprueba un presupuesto específico actualizando:
    - pre_vbgg = 1 (aprobado)
    - pre_vbggDt = fecha actual
    - pre_vbggTime = hora actual
    - pre_vbggUsu = usuario autenticado (del token JWT)
    
    **Requiere autenticación:** Token JWT en header Authorization.
    """,
    tags=["Presupuestos"]
)
async def aprobar_presupuesto(
    data: PresupuestoAprobar,
    db: Session = Depends(get_tenant_db),
    usuario: str = Depends(get_current_user_id)
) -> PresupuestoAprobadoResponse:
    """
    Aprueba un presupuesto.
    
    Args:
        data: Datos del presupuesto a aprobar (Loc_cod, pre_nro, usuario)
        db: Sesión de base de datos (inyectada automáticamente)
        
    Returns:
        PresupuestoAprobadoResponse: Confirmación de aprobación con datos actualizados
        
    Raises:
        HTTPException 404: Si el presupuesto no existe
        HTTPException 500: Si hay error en la base de datos
        
    Example:
        POST /api/v1/presupuestos/aprobar
        {
            "Loc_cod": 1,
            "pre_nro": 12345,
            "usuario": "admin"
        }
    """
    try:
        resultado = PresupuestoService.aprobar_presupuesto(
            db,
            loc_cod=data.Loc_cod,
            pre_nro=data.pre_nro,
            usuario=usuario
        )
        
        return PresupuestoAprobadoResponse(
            success=True,
            message="Presupuesto aprobado exitosamente",
            **resultado
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al aprobar presupuesto: {str(e)}"
        )


@router.post(
    "/anular",
    response_model=PresupuestoAprobadoResponse,
    status_code=status.HTTP_200_OK,
    summary="Anular presupuesto",
    tags=["Presupuestos"]
)
async def anular_presupuesto(
    data: PresupuestoAprobar,
    db: Session = Depends(get_tenant_db),
    usuario: str = Depends(get_current_user_id)
) -> PresupuestoAprobadoResponse:
    from datetime import date as date_type
    try:
        resultado = PresupuestoService.anular_presupuesto(
            db,
            loc_cod=data.Loc_cod,
            pre_nro=data.pre_nro,
        )
        return PresupuestoAprobadoResponse(
            success=True,
            message="Presupuesto anulado exitosamente",
            Loc_cod=resultado["Loc_cod"],
            pre_nro=resultado["pre_nro"],
            pre_vbggUsu="",
            pre_vbggDt=date_type.today(),
            pre_vbggTime=""
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al anular presupuesto: {str(e)}"
        )


@router.post(
    "/desaprobar",
    response_model=PresupuestoAprobadoResponse,
    status_code=status.HTTP_200_OK,
    summary="Desaprobar presupuesto",
    description="""
    Desaprueba un presupuesto específico revirtiendo sus estados:
    - pre_vbgg = 0 (pendiente)
    - pre_vbggDt = fecha original
    - pre_vbggTime = vacío
    - pre_vbggUsu = vacío
    
    **Requiere autenticación:** Token JWT en header Authorization.
    """,
    tags=["Presupuestos"]
)
async def desaprobar_presupuesto(
    data: PresupuestoAprobar,
    db: Session = Depends(get_tenant_db),
    usuario: str = Depends(get_current_user_id)
) -> PresupuestoAprobadoResponse:
    """
    Desaprueba un presupuesto.
    """
    try:
        resultado = PresupuestoService.desaprobar_presupuesto(
            db,
            loc_cod=data.Loc_cod,
            pre_nro=data.pre_nro,
            usuario=usuario
        )
        
        # Como respuesta usamos el mismo modelo pero con datos revertidos
        return PresupuestoAprobadoResponse(
            success=True,
            message="Presupuesto desaprobado exitosamente",
            Loc_cod=resultado["Loc_cod"],
            pre_nro=resultado["pre_nro"],
            pre_vbggUsu="",
            pre_vbggDt=resultado.get("pre_vbggDt") or resultado.get("pre_fec"), # fallback
            pre_vbggTime=""
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al desaprobar presupuesto: {str(e)}"
        )
