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
    service = OrdenCompraService()
    return service.obtener_indicadores(db, current_user)

@router.get("/pendientes", response_model=List[OrdenCompraDetalle])
async def obtener_pendientes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user_id)
) -> Any:
    """
    Obtener órdenes pendientes con validación PDF.
    Filtro: ocp_A1_Ap=1 AND ocp_A2_Ap=0 (liberadas pero no aprobadas)
    """
    service = OrdenCompraService()
    return await service.obtener_pendientes_con_pdf(db, skip=skip, limit=limit)

@router.get("/aprobadas", response_model=List[OrdenCompraDetalle])
async def obtener_aprobadas(
    usuario: str = Query(None, description="Usuario que aprobó (opcional)"),
    fecha_desde: date = Query(None, description="Fecha desde (opcional)"),
    fecha_hasta: date = Query(None, description="Fecha hasta (opcional)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user_id)
) -> Any:
    """
    Obtener órdenes aprobadas con validación PDF.
    Si no se especifica usuario/fechas: solo las aprobadas hoy
    """
    service = OrdenCompraService()
    return await service.obtener_aprobadas_con_pdf(
        db, 
        usuario or None, 
        fecha_desde, 
        fecha_hasta,
        skip=skip,
        limit=limit
    )

@router.post("/aprobar", response_model=OrdenCompraAprobadoResponse)
def aprobar_orden(
    orden_in: OrdenCompraAprobar,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user_id)
) -> Any:
    """
    Aprobar una orden de compra (nivel 2 - aprobación final).
    """
    service = OrdenCompraService()
    orden = service.aprobar_orden(
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
        new_status="aprobada"
    )

@router.post("/desaprobar", response_model=OrdenCompraAprobadoResponse)
def desaprobar_orden(
    orden_in: OrdenCompraAprobar,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user_id)
) -> Any:
    """
    Deshacer aprobación de una orden de compra (nivel 2).
    """
    service = OrdenCompraService()
    orden = service.desaprobar_orden(
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
