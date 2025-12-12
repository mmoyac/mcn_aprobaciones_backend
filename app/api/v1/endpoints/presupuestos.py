"""
Endpoints REST API para gestión de presupuestos
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.core.deps import get_current_user, get_current_user_id
from app.models.usuario import Usuario
from app.schemas.presupuesto import (
    PresupuestoIndicadores,
    PresupuestoDetalle,
    PresupuestoAprobar,
    PresupuestoAprobadoResponse
)
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
    db: Session = Depends(get_db),
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
    limit: int = 100,
    db: Session = Depends(get_db),
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
    if limit > 1000:
        raise HTTPException(
            status_code=400,
            detail="El límite máximo es 1000 registros"
        )
    
    try:
        presupuestos = PresupuestoService.obtener_presupuestos_pendientes(
            db, skip=skip, limit=limit
        )
        return presupuestos
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
    db: Session = Depends(get_db),
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
        return presupuestos
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener presupuestos aprobados: {str(e)}"
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
    db: Session = Depends(get_db),
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
    db: Session = Depends(get_db),
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
