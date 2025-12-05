"""
Endpoints REST API para gestión de presupuestos
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.presupuesto import (
    PresupuestoIndicadores,
    PresupuestoDetalle
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
      (Pre_vbLib = 1 AND pre_vbgg = 0)
    - **Aprobados**: Presupuestos aprobados por gerencia general
      (pre_vbgg = 1)
    
    Estos indicadores son útiles para dashboards y reportes ejecutivos.
    """,
    tags=["Indicadores"]
)
async def obtener_indicadores(
    db: Session = Depends(get_db)
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
    db: Session = Depends(get_db)
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
    summary="Listar presupuestos aprobados",
    description="""
    Retorna el listado de presupuestos aprobados por gerencia.
    
    Criterio: pre_vbgg = 1
    
    Soporta paginación mediante parámetros skip y limit.
    """,
    tags=["Presupuestos"]
)
async def listar_presupuestos_aprobados(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> List[PresupuestoDetalle]:
    """
    Lista presupuestos aprobados con paginación.
    
    Args:
        skip: Número de registros a omitir (default: 0)
        limit: Cantidad máxima de registros a retornar (default: 100, max: 1000)
        db: Sesión de base de datos (inyectada automáticamente)
        
    Returns:
        List[PresupuestoDetalle]: Lista de presupuestos aprobados
        
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
        presupuestos = PresupuestoService.obtener_presupuestos_aprobados(
            db, skip=skip, limit=limit
        )
        return presupuestos
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener presupuestos aprobados: {str(e)}"
        )
