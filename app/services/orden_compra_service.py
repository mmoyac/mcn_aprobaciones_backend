from sqlalchemy.orm import Session
from sqlalchemy import text, and_, func
from datetime import date, datetime
from typing import List, Optional

from app.models.orden_compra import OrdenCompra
from app.schemas.orden_compra import OrdenCompraIndicadores

class OrdenCompraService:
    @staticmethod
    def obtener_indicadores(db: Session, user_id: str) -> OrdenCompraIndicadores:
        """
        Retorna los indicadores para el dashboard:
        - Pendientes: Total de órdenes sin aprobar (ocp_A1_Ap=0) y vigentes (ocp_pdt != 'N' y != ' ')
        - Aprobados Hoy: Total aprobados por el usuario hoy
        """
        # Contar pendientes
        pendientes = db.query(func.count(OrdenCompra.ocp_nro)).filter(
            and_(
                OrdenCompra.ocp_A1_Ap == 0,
                OrdenCompra.ocp_pdt != 'N',
                OrdenCompra.ocp_pdt != ' '
            )
        ).scalar() or 0

        # Contar aprobados hoy por el usuario
        hoy = date.today()
        aprobados_hoy = db.query(func.count(OrdenCompra.ocp_nro)).filter(
            and_(
                OrdenCompra.ocp_A1_Ap == 1,
                func.lower(OrdenCompra.ocp_A1_Usu) == func.lower(user_id),
                OrdenCompra.ocp_A1_Dt == hoy
            )
        ).scalar() or 0

        return OrdenCompraIndicadores(
            pendientes_count=pendientes,
            aprobados_hoy_count=aprobados_hoy
        )

    @staticmethod
    def obtener_pendientes(db: Session, skip: int = 0, limit: int = 100) -> List[OrdenCompra]:
        """
        Retorna la lista de órdenes de compra pendientes de aprobación.
        Filtro: ocp_A1_Ap = 0 AND ocp_pdt NOT IN ('N', ' ')
        """
        return db.query(OrdenCompra).filter(
            and_(
                OrdenCompra.ocp_A1_Ap == 0,
                OrdenCompra.ocp_pdt != 'N',
                OrdenCompra.ocp_pdt != ' '
            )
        ).order_by(OrdenCompra.ocp_fec.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def obtener_aprobados(
        db: Session, 
        user_id: str, 
        fecha_desde: date, 
        fecha_hasta: date,
        skip: int = 0, 
        limit: int = 100
    ) -> List[OrdenCompra]:
        """
        Retorna la lista de órdenes aprobadas por un usuario en un rango de fechas.
        """
        return db.query(OrdenCompra).filter(
            and_(
                OrdenCompra.ocp_A1_Ap == 1,
                func.lower(OrdenCompra.ocp_A1_Usu) == func.lower(user_id),
                OrdenCompra.ocp_A1_Dt >= fecha_desde,
                OrdenCompra.ocp_A1_Dt <= fecha_hasta
            )
        ).order_by(OrdenCompra.ocp_A1_Dt.desc(), OrdenCompra.ocp_A1_Hr.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def aprobar_orden(db: Session, ocp_nro: int, loc_cod: int, user_id: str) -> Optional[OrdenCompra]:
        orden = db.query(OrdenCompra).filter(
            and_(
                OrdenCompra.ocp_nro == ocp_nro,
                OrdenCompra.Loc_cod == loc_cod
            )
        ).first()

        if not orden:
            return None

        # Actualizar campos de aprobación
        now = datetime.now()
        orden.ocp_A1_Ap = 1
        orden.ocp_A1_Usu = user_id
        orden.ocp_A1_Dt = now.date()
        orden.ocp_A1_Hr = now.strftime("%H:%M:%S")

        db.commit()
        db.refresh(orden)
        return orden

    @staticmethod
    def desaprobar_orden(db: Session, ocp_nro: int, loc_cod: int) -> Optional[OrdenCompra]:
        orden = db.query(OrdenCompra).filter(
            and_(
                OrdenCompra.ocp_nro == ocp_nro,
                OrdenCompra.Loc_cod == loc_cod
            )
        ).first()

        if not orden:
            return None

        # Reset campos de aprobación
        # Importante: Mantener integridad con campos NOT NULL
        # Usamos ocp_fec como fecha fallback y string vacío para hora
        orden.ocp_A1_Ap = 0
        orden.ocp_A1_Usu = ''
        orden.ocp_A1_Dt = orden.ocp_fec 
        orden.ocp_A1_Hr = ''

        db.commit()
        db.refresh(orden)
        return orden
