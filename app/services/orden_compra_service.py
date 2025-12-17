from sqlalchemy.orm import Session
from sqlalchemy import text, and_, func
from datetime import date, datetime
import pytz
from typing import List, Optional
import logging

from app.models.orden_compra import OrdenCompra
from app.schemas.orden_compra import OrdenCompraIndicadores, OrdenCompraDetalle
from app.core.config import settings

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Timezone de Chile
chile_tz = pytz.timezone('America/Santiago')

class OrdenCompraService:
    @staticmethod
    def obtener_indicadores(db: Session, user_id: str) -> OrdenCompraIndicadores:
        """
        Retorna los indicadores para el dashboard:
        - Total: Todas las órdenes vigentes 
        - Pendientes: ocp_A1_Ap=0 AND ocp_pdt<>'N' AND ocp_pdt<>' ' (sin aprobar en nivel 1)
        - Aprobadas: ocp_A2_Ap=1 (aprobadas finalmente)
        """
        # Total de órdenes vigentes
        total = db.query(func.count(OrdenCompra.ocp_nro)).filter(
            and_(
                OrdenCompra.ocp_pdt != 'N',
                OrdenCompra.ocp_pdt != '',
                OrdenCompra.ocp_pdt.isnot(None)
            )
        ).scalar() or 0

        # Pendientes: Sin aprobar en nivel 1, estado válido
        pendientes = db.query(func.count(OrdenCompra.ocp_nro)).filter(
            and_(
                OrdenCompra.ocp_A1_Ap == 0,
                OrdenCompra.ocp_pdt != 'N',
                OrdenCompra.ocp_pdt != '',
                OrdenCompra.ocp_pdt.isnot(None)
            )
        ).scalar() or 0

        # Aprobadas finalmente
        aprobadas = db.query(func.count(OrdenCompra.ocp_nro)).filter(
            OrdenCompra.ocp_A2_Ap == 1
        ).scalar() or 0

        return OrdenCompraIndicadores(
            total=total,
            pendientes=pendientes,
            aprobadas=aprobadas
        )

    async def _verificar_pdf_existe(self, loc_cod: int, ocp_nro: int) -> int:
        """
        Verifica si existe un PDF para la orden de compra.
        CLAVE: Usa tipo=2 para órdenes de compra (diferente de presupuestos que usan tipo=1)
        
        Returns:
            1 si existe PDF, 0 si no existe
        """
        try:
            from app.db.session_postgres import get_postgres_db_sync
            
            postgres_session = get_postgres_db_sync()
            
            try:
                query = text("""
                    SELECT COUNT(*) as count 
                    FROM documentos_pdf 
                    WHERE numero = :numero 
                    AND tipo = 2
                """)
                
                result = postgres_session.execute(query, {
                    'numero': ocp_nro
                })
                
                count = result.fetchone()
                return 1 if count and count[0] > 0 else 0
                
            finally:
                postgres_session.close()
                
        except Exception as e:
            logger.error(f"Error verificando PDF para orden {ocp_nro}: {str(e)}")
            return 0

    async def obtener_pendientes_con_pdf(self, db: Session, skip: int = 0, limit: int = 100) -> List[OrdenCompraDetalle]:
        """
        Retorna órdenes pendientes con validación PDF.
        Filtro: ocp_A1_Ap=0 AND ocp_pdt<>'N' AND ocp_pdt<>' ' (sin aprobar en nivel 1)
        """
        try:
            # Consulta con JOIN a proveedor
            ordenes = db.query(OrdenCompra).filter(
                and_(
                    OrdenCompra.ocp_A1_Ap == 0,
                    OrdenCompra.ocp_pdt != 'N',
                    OrdenCompra.ocp_pdt != '',
                    OrdenCompra.ocp_pdt.isnot(None)
                )
            ).order_by(OrdenCompra.ocp_fec.desc()).offset(skip).limit(limit).all()

            # Enriquecer con información PDF
            ordenes_detalle = []
            for orden in ordenes:
                # Verificar PDF
                tiene_pdf = await self._verificar_pdf_existe(orden.Loc_cod, orden.ocp_nro)
                
                # Crear objeto OrdenCompraDetalle
                orden_detalle = OrdenCompraDetalle(
                    Loc_cod=orden.Loc_cod,
                    ocp_nro=orden.ocp_nro,
                    ocp_fec=orden.ocp_fec,
                    pro_rut=orden.pro_rut,
                    ocp_pdt=orden.ocp_pdt,
                    ocp_net=orden.ocp_net,
                    ocp_iva=orden.ocp_iva,
                    ocp_ila=orden.ocp_ila,
                    ocp_fee=orden.ocp_fee,
                    proveedor_nombre=orden.proveedor_nombre,
                    monto_total=orden.monto_total,
                    tienepdf=tiene_pdf
                )
                ordenes_detalle.append(orden_detalle)

            return ordenes_detalle
            
        except Exception as e:
            logger.error(f"Error obteniendo órdenes pendientes: {str(e)}")
            raise

    async def obtener_aprobadas_con_pdf(
        self,
        db: Session, 
        user_id: str = None, 
        fecha_desde: date = None, 
        fecha_hasta: date = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[OrdenCompraDetalle]:
        """
        Retorna órdenes aprobadas con validación PDF.
        Si no se especifica usuario: todas las aprobadas hoy
        Si se especifica usuario y fechas: las del usuario en ese rango
        """
        try:
            # Construir filtros base
            filters = [OrdenCompra.ocp_A2_Ap == 1]
            
            # Si no hay usuario específico, mostrar solo las de hoy
            if user_id is None:
                hoy_chile = datetime.now(chile_tz).date()
                filters.append(OrdenCompra.ocp_A2_Dt == hoy_chile)
            else:
                # Filtrar por usuario y fechas
                filters.append(func.lower(OrdenCompra.ocp_A2_Usu) == func.lower(user_id))
                if fecha_desde:
                    filters.append(OrdenCompra.ocp_A2_Dt >= fecha_desde)
                if fecha_hasta:
                    filters.append(OrdenCompra.ocp_A2_Dt <= fecha_hasta)

            ordenes = db.query(OrdenCompra).filter(
                and_(*filters)
            ).order_by(OrdenCompra.ocp_A2_Dt.desc(), OrdenCompra.ocp_A2_Hr.desc()).offset(skip).limit(limit).all()

            # Enriquecer con información PDF
            ordenes_detalle = []
            for orden in ordenes:
                # Verificar PDF
                tiene_pdf = await self._verificar_pdf_existe(orden.Loc_cod, orden.ocp_nro)
                
                # Crear objeto OrdenCompraDetalle
                orden_detalle = OrdenCompraDetalle(
                    Loc_cod=orden.Loc_cod,
                    ocp_nro=orden.ocp_nro,
                    ocp_fec=orden.ocp_fec,
                    pro_rut=orden.pro_rut,
                    ocp_pdt=orden.ocp_pdt,
                    ocp_net=orden.ocp_net,
                    ocp_iva=orden.ocp_iva,
                    ocp_ila=orden.ocp_ila,
                    ocp_fee=orden.ocp_fee,
                    proveedor_nombre=orden.proveedor_nombre,
                    monto_total=orden.monto_total,
                    tienepdf=tiene_pdf,
                    ocp_A2_Usu=orden.ocp_A2_Usu,
                    ocp_A2_Dt=orden.ocp_A2_Dt,
                    ocp_A2_Hr=orden.ocp_A2_Hr
                )
                ordenes_detalle.append(orden_detalle)

            return ordenes_detalle
            
        except Exception as e:
            logger.error(f"Error obteniendo órdenes aprobadas: {str(e)}")
            raise

    def aprobar_orden(self, db: Session, ocp_nro: int, loc_cod: int, user_id: str) -> Optional[OrdenCompra]:
        """
        Aprueba una orden de compra (nivel 2 - equivalente a pre_vbgg)
        """
        orden = db.query(OrdenCompra).filter(
            and_(
                OrdenCompra.ocp_nro == ocp_nro,
                OrdenCompra.Loc_cod == loc_cod
            )
        ).first()

        if not orden:
            return None

        # Actualizar campos de aprobación nivel 2 (final)
        now_chile = datetime.now(chile_tz)
        orden.ocp_A2_Ap = 1
        orden.ocp_A2_Usu = user_id
        orden.ocp_A2_Dt = now_chile.date()
        orden.ocp_A2_Hr = now_chile.strftime("%H:%M:%S")

        db.commit()
        db.refresh(orden)
        return orden

    def desaprobar_orden(self, db: Session, ocp_nro: int, loc_cod: int) -> Optional[OrdenCompra]:
        """
        Deshace la aprobación de una orden (nivel 2)
        """
        orden = db.query(OrdenCompra).filter(
            and_(
                OrdenCompra.ocp_nro == ocp_nro,
                OrdenCompra.Loc_cod == loc_cod
            )
        ).first()

        if not orden:
            return None

        # Reset campos de aprobación nivel 2
        # Mantener integridad con campos NOT NULL
        orden.ocp_A2_Ap = 0
        orden.ocp_A2_Usu = ''
        orden.ocp_A2_Dt = orden.ocp_fec  # Fecha fallback
        orden.ocp_A2_Hr = ''

        db.commit()
        db.refresh(orden)
        return orden
