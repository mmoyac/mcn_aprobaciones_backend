from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date

from app.db.session import get_db
from app.core.deps import get_current_user_id
from app.schemas.orden_compra import (
    OrdenCompraDetalle,
    OrdenCompraIndicadores,
    OrdenCompraAprobar,
    OrdenCompraAprobadoResponse
)
from app.services.orden_compra_service import OrdenCompraService

router = APIRouter()

@router.get("/indicadores", response_model=OrdenCompraIndicadores)
def obtener_indicadores(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user_id)
) -> Any:
    """
    Obtener indicadores del dashboard para órdenes de compra.
    """
    return OrdenCompraService.obtener_indicadores(db, current_user)

@router.get("/pendientes", response_model=List[OrdenCompraDetalle])
def obtener_pendientes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user_id)
) -> Any:
    """
    Obtener listado de órdenes de compra pendientes de aprobación.
    """
    pendientes = OrdenCompraService.obtener_pendientes(db, skip=skip, limit=limit)
    return pendientes

@router.get("/aprobados", response_model=List[OrdenCompraDetalle])
def obtener_aprobados(
    fecha_desde: date,
    fecha_hasta: date,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user_id)
) -> Any:
    """
    Obtener listado de órdenes aprobadas por el usuario actual en un rango de fechas.
    """
    return OrdenCompraService.obtener_aprobados(
        db, 
        current_user, 
        fecha_desde, 
        fecha_hasta
    )

@router.post("/aprobar", response_model=OrdenCompraAprobadoResponse)
def aprobar_orden(
    orden_in: OrdenCompraAprobar,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user_id)
) -> Any:
    """
    Aprobar una orden de compra.
    """
    orden = OrdenCompraService.aprobar_orden(
        db, 
        orden_in.ocp_nro, 
        orden_in.Loc_cod, 
        current_user
    )
    
    if not orden:
        raise HTTPException(
            status_code=404, 
            detail="La orden de compra no existe"
        )
        
    return OrdenCompraAprobadoResponse(
        message="Orden aprobada exitosamente",
        ocp_nro=orden.ocp_nro,
        new_status="aprobado"
    )

@router.post("/desaprobar", response_model=OrdenCompraAprobadoResponse)
def desaprobar_orden(
    orden_in: OrdenCompraAprobar,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user_id)
) -> Any:
    """
    Deshacer aprobación de una orden de compra.
    """
    orden = OrdenCompraService.desaprobar_orden(
        db, 
        orden_in.ocp_nro, 
        orden_in.Loc_cod
    )
    
    if not orden:
        raise HTTPException(
            status_code=404, 
            detail="La orden de compra no existe"
        )
        
    return OrdenCompraAprobadoResponse(
        message="Aprobación deshecha exitosamente",
        ocp_nro=orden.ocp_nro,
        new_status="pendiente"
    )
