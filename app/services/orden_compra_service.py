from sqlalchemy.orm import Session
from sqlalchemy import text, and_, func
from datetime import date, datetime
import pytz
import os
from typing import List, Optional
import logging

from app.models.orden_compra import OrdenCompra
from app.models.local import Local
from app.schemas.orden_compra import OrdenCompraIndicadores, OrdenCompraDetalle, DetalleOrdenCompra, AprobacionOrdenCompra, ItemOrdenCompra
from app.db.tenant_session import create_tenant_session

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Timezone de Chile
chile_tz = pytz.timezone('America/Santiago')

class OrdenCompraService:

    def _get_reppdf_session(self):
        """Crea sesión a lexascl_reppdf usando env vars. Retorna None si no hay credenciales."""
        host = os.getenv("REPPDF_HOST", "179.27.210.204")
        port = int(os.getenv("REPPDF_PORT", "3306"))
        db_name = os.getenv("REPPDF_DB", "lexascl_reppdf")
        user = os.getenv("REPPDF_USER")
        password = os.getenv("REPPDF_PASSWORD")
        if not user or not password:
            return None
        return create_tenant_session(
            db_host=host, db_port=port, db_name=db_name,
            db_user=user, db_password=password
        )

    def _verificar_pdfs_batch(self, items: list, tenant_id: int) -> dict:
        """
        Consulta en una sola query todos los PDFs para una lista de (loc_cod, numero).
        Retorna dict {(loc_cod, numero): estado} donde estado: 0=no existe, 1=con PDF, 2=sin contenido.
        """
        if not items:
            return {}
        db_cliente = self._get_reppdf_session()
        if not db_cliente:
            return {}
        try:
            numeros = [numero for _, numero in items]
            in_clause = ",".join(str(n) for n in numeros)
            result = db_cliente.execute(
                text(f"""
                    SELECT PdfLocCod, PdfNumero, LENGTH(PdfBlob) as blob_size
                    FROM pdf001
                    WHERE PdfEmpCd = :emp_cd
                      AND PdfTipo   = 2
                      AND PdfNumero IN ({in_clause})
                """),
                {"emp_cd": tenant_id}
            )
            rows = result.fetchall()
            pdf_map = {}
            for row in rows:
                key = (row[0], row[1])
                blob_size = row[2] or 0
                pdf_map[key] = 1 if blob_size > 0 else 2
            for loc_cod, numero in items:
                if (loc_cod, numero) not in pdf_map:
                    pdf_map[(loc_cod, numero)] = 0
            return pdf_map
        except Exception as e:
            logger.error(f"Error en batch PDF query: {str(e)}")
            return {}
        finally:
            db_cliente.close()

    def _eliminar_pdf_reppdf(self, loc_cod: int, ocp_nro: int, tenant_id: int) -> None:
        """Elimina el PDF de pdf001 en REPPDF al aprobar una orden de compra. Falla silenciosamente."""
        db_cliente = self._get_reppdf_session()
        if not db_cliente:
            return
        try:
            result = db_cliente.execute(
                text("""
                    DELETE FROM pdf001
                    WHERE PdfEmpCd = :emp_cd
                      AND PdfTipo   = 2
                      AND PdfLocCod = :loc_cod
                      AND PdfNumero = :numero
                """),
                {"emp_cd": tenant_id, "loc_cod": loc_cod, "numero": ocp_nro}
            )
            db_cliente.commit()
            logger.info(f"PDF eliminado de REPPDF: tenant={tenant_id}, loc_cod={loc_cod}, ocp_nro={ocp_nro}, filas={result.rowcount}")
        except Exception as e:
            logger.error(f"Error al eliminar PDF de REPPDF para orden {ocp_nro}: {e}", exc_info=True)
        finally:
            db_cliente.close()

    async def _verificar_pdf_existe(self, loc_cod: int, ocp_nro: int, tenant_id: int) -> int:
        result = self._verificar_pdfs_batch([(loc_cod, ocp_nro)], tenant_id)
        return result.get((loc_cod, ocp_nro), 0)

    def obtener_indicadores(self, db: Session, user_id: str = None) -> OrdenCompraIndicadores:
        """
        Retorna los indicadores para el dashboard:
        - Total: Todas las órdenes vigentes
        - Pendientes: ocp_A1_Ap=1 AND ocp_A2_Ap=0 (liberadas pero no aprobadas)
        - Aprobadas: ocp_A2_Ap=1 (aprobadas finalmente)
        """
        total = db.query(func.count(OrdenCompra.ocp_nro)).filter(
            and_(
                OrdenCompra.ocp_pdt != 'N',
                OrdenCompra.ocp_pdt != '',
                OrdenCompra.ocp_pdt.isnot(None)
            )
        ).scalar() or 0

        pendientes = db.query(func.count(OrdenCompra.ocp_nro)).filter(
            and_(
                OrdenCompra.ocp_A1_Ap == 0,
                OrdenCompra.ocp_A2_Ap == 1,
                OrdenCompra.ocp_pdt.in_(['T', 'I', 'N'])
            )
        ).scalar() or 0

        aprobadas = db.query(func.count(OrdenCompra.ocp_nro)).filter(
            OrdenCompra.ocp_A1_Ap == 1
        ).scalar() or 0

        return OrdenCompraIndicadores(
            total=total,
            pendientes=pendientes,
            aprobadas=aprobadas
        )

    async def _verificar_pdf_existe(self, loc_cod: int, ocp_nro: int, tenant_id: int) -> int:
        """
        Verifica si existe PDF en la tabla pdf001 del cliente (lexascl_reppdf).
        Retorna: 0 = no existe, 1 = existe con PDF, 2 = existe sin PDF (blob vacío)
        CLAVE: Usa tipo=2 para órdenes de compra.
        """
        host = os.getenv("REPPDF_HOST", "179.27.210.204")
        port = int(os.getenv("REPPDF_PORT", "3306"))
        db_name = os.getenv("REPPDF_DB", "lexascl_reppdf")
        user = os.getenv("REPPDF_USER")
        password = os.getenv("REPPDF_PASSWORD")
        if not user or not password:
            return 0
        db_cliente = None
        try:
            db_cliente = create_tenant_session(
                db_host=host,
                db_port=port,
                db_name=db_name,
                db_user=user,
                db_password=password
            )
            result = db_cliente.execute(
                text("""
                    SELECT LENGTH(PdfBlob) as blob_size FROM pdf001
                    WHERE PdfEmpCd = :emp_cd
                      AND PdfLocCod = :loc_cod
                      AND PdfTipo   = 2
                      AND PdfNumero = :numero
                    LIMIT 1
                """),
                {"emp_cd": tenant_id, "loc_cod": loc_cod, "numero": ocp_nro}
            )
            row = result.fetchone()
            if row is None:
                return 0
            blob_size = row[0] or 0
            return 1 if blob_size > 0 else 2
        except Exception as e:
            logger.error(f"Error verificando PDF para orden {ocp_nro}: {str(e)}")
            return 0
        finally:
            if db_cliente:
                db_cliente.close()

    async def obtener_pendientes_con_pdf(self, db: Session, skip: int = 0, limit: int = 100, tenant_id: int = 1) -> List[OrdenCompraDetalle]:
        """
        Retorna órdenes pendientes con validación PDF.
        Filtro: ocp_A1_Ap=0 AND ocp_pdt<>'N' AND ocp_pdt<>' ' (sin aprobar en nivel 1)
        """
        try:
            # Consulta con JOIN a proveedor
            ordenes = db.query(OrdenCompra, Local.Loc_des).outerjoin(
                Local, OrdenCompra.Loc_cod == Local.Loc_cod
            ).filter(
                and_(
                    OrdenCompra.ocp_A1_Ap == 0,
                    OrdenCompra.ocp_A2_Ap == 1,
                    OrdenCompra.ocp_pdt.in_(['T', 'I', 'N'])
                )
            ).order_by(OrdenCompra.ocp_fec.desc()).offset(skip).limit(limit).all()

            # Batch query: una sola consulta para todos los PDFs
            items = [(o.Loc_cod, o.ocp_nro) for o, _ in ordenes]
            pdf_map = self._verificar_pdfs_batch(items, tenant_id)

            # Enriquecer con información PDF y sucursal
            ordenes_detalle = []
            for orden, loc_des in ordenes:
                tiene_pdf = pdf_map.get((orden.Loc_cod, orden.ocp_nro), 0)

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
                    loc_des=loc_des,
                    ocp_A4_Ap=orden.ocp_A4_Ap or 0,
                    ocp_A4_Usu=(orden.ocp_A4_Usu or '').strip() or None,
                    ocp_A3_Anu=orden.ocp_A3_Anu or 0,
                    ocp_A3_Usu=(orden.ocp_A3_Usu or '').strip() or None,
                    ocp_A2_Ap=orden.ocp_A2_Ap or 0,
                    ocp_A2_Usu=(orden.ocp_A2_Usu or '').strip() or None,
                    ocp_A1_Ap=orden.ocp_A1_Ap or 0,
                    ocp_A1_Usu=(orden.ocp_A1_Usu or '').strip() or None,
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
        limit: int = 100,
        tenant_id: int = 1
    ) -> List[OrdenCompraDetalle]:
        """
        Retorna órdenes aprobadas con validación PDF.
        Si no se especifica usuario: todas las aprobadas hoy
        Si se especifica usuario y fechas: las del usuario en ese rango
        """
        try:
            # Construir filtros base
            filters = [OrdenCompra.ocp_A1_Ap == 1]

            # Si no hay usuario específico, mostrar solo las de hoy
            if user_id is None:
                hoy_chile = datetime.now(chile_tz).date()
                filters.append(OrdenCompra.ocp_A1_Dt == hoy_chile)
            else:
                # Filtrar por usuario y fechas
                filters.append(func.lower(OrdenCompra.ocp_A1_Usu) == func.lower(user_id))
                if fecha_desde:
                    filters.append(OrdenCompra.ocp_A1_Dt >= fecha_desde)
                if fecha_hasta:
                    filters.append(OrdenCompra.ocp_A1_Dt <= fecha_hasta)

            ordenes = db.query(OrdenCompra).filter(
                and_(*filters)
            ).order_by(OrdenCompra.ocp_A1_Dt.desc(), OrdenCompra.ocp_A1_Hr.desc()).offset(skip).limit(limit).all()

            # Batch query: una sola consulta para todos los PDFs
            items = [(o.Loc_cod, o.ocp_nro) for o in ordenes]
            pdf_map = self._verificar_pdfs_batch(items, tenant_id)

            # Enriquecer con información PDF
            ordenes_detalle = []
            for orden in ordenes:
                # Verificar PDF
                tiene_pdf = pdf_map.get((orden.Loc_cod, orden.ocp_nro), 0)
                
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
                    ocp_A4_Ap=orden.ocp_A4_Ap or 0,
                    ocp_A4_Usu=(orden.ocp_A4_Usu or '').strip() or None,
                    ocp_A3_Anu=orden.ocp_A3_Anu or 0,
                    ocp_A3_Usu=(orden.ocp_A3_Usu or '').strip() or None,
                    ocp_A2_Ap=orden.ocp_A2_Ap or 0,
                    ocp_A2_Usu=(orden.ocp_A2_Usu or '').strip() or None,
                    ocp_A2_Dt=orden.ocp_A1_Dt,
                    ocp_A2_Hr=(orden.ocp_A1_Hr or '').strip() or None,
                    ocp_A1_Ap=orden.ocp_A1_Ap or 0,
                    ocp_A1_Usu=(orden.ocp_A1_Usu or '').strip() or None,
                )
                ordenes_detalle.append(orden_detalle)

            return ordenes_detalle
            
        except Exception as e:
            logger.error(f"Error obteniendo órdenes aprobadas: {str(e)}")
            raise

    def obtener_detalle(self, db: Session, loc_cod: int, ocp_nro: int) -> Optional[DetalleOrdenCompra]:
        def _fecha(val):
            if not val:
                return None
            if isinstance(val, date) and val.year < 1900:
                return None
            return val

        def _str(val):
            return val.strip() or None if val else None

        orden = db.query(OrdenCompra, Local.Loc_des).outerjoin(
            Local, OrdenCompra.Loc_cod == Local.Loc_cod
        ).filter(
            and_(OrdenCompra.Loc_cod == loc_cod, OrdenCompra.ocp_nro == ocp_nro)
        ).first()

        if not orden:
            return None

        oc, loc_des = orden
        return DetalleOrdenCompra(
            Loc_cod=oc.Loc_cod,
            ocp_nro=oc.ocp_nro,
            ocp_fec=oc.ocp_fec,
            ocp_fee=oc.ocp_fee,
            pro_rut=oc.pro_rut,
            proveedor_nombre=oc.proveedor_nombre,
            ocp_pdt=oc.ocp_pdt,
            ocp_net=oc.ocp_net,
            ocp_iva=oc.ocp_iva,
            ocp_ila=oc.ocp_ila,
            monto_total=oc.monto_total,
            loc_des=loc_des,
            aprobaciones=AprobacionOrdenCompra(
                ocp_a4usu=_str(oc.ocp_A4_Usu),
                ocp_a4_dt=_fecha(oc.ocp_A4_Dt),
                ocp_a4_hr=_str(oc.ocp_A4_Hr),
                ocp_a3usu=_str(oc.ocp_A3_Usu),
                ocp_a3_dt=_fecha(oc.ocp_A3_Dt),
                ocp_a3_hr=_str(oc.ocp_A3_Hr),
                ocp_a2usu=_str(oc.ocp_A2_Usu),
                ocp_a2_dt=_fecha(oc.ocp_A2_Dt),
                ocp_a2_hr=_str(oc.ocp_A2_Hr),
                ocp_a1usu=_str(oc.ocp_A1_Usu),
                ocp_a1_dt=_fecha(oc.ocp_A1_Dt),
                ocp_a1_hr=_str(oc.ocp_A1_Hr),
            )
        )

    def obtener_items(self, db: Session, loc_cod: int, ocp_nro: int) -> List[ItemOrdenCompra]:
        result = db.execute(
            text("""
                SELECT Loc_cod, ocp_nro, ocp_lin, ocp_mat, mat_des,
                       Ocp_Odt, Ocp_De1, Ocp_De2, Ocp_De3, Ocp_est, Ocp_can, Ocp_pre
                FROM adq005
                INNER JOIN COT012 ON ocp_mat = mat_cod
                WHERE ocp_nro = :ocp_nro AND loc_cod = :loc_cod
                ORDER BY ocp_lin
            """),
            {"ocp_nro": ocp_nro, "loc_cod": loc_cod}
        )
        rows = result.fetchall()
        return [
            ItemOrdenCompra(
                Loc_cod=row[0],
                ocp_nro=row[1],
                ocp_lin=row[2],
                ocp_mat=row[3].strip() if row[3] else None,
                mat_des=row[4].strip() if row[4] else None,
                Ocp_Odt=row[5],
                Ocp_De1=row[6].strip() if row[6] else None,
                Ocp_De2=row[7].strip() if row[7] else None,
                Ocp_De3=row[8].strip() if row[8] else None,
                Ocp_est=row[9].strip() if row[9] else None,
                Ocp_can=float(row[10]) if row[10] is not None else None,
                Ocp_pre=int(row[11]) if row[11] is not None else None,
            )
            for row in rows
        ]

    def aprobar_orden(self, db: Session, ocp_nro: int, loc_cod: int, user_id: str, tenant_id: int = 1) -> Optional[OrdenCompra]:
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

        now_chile = datetime.now(chile_tz)
        orden.ocp_A1_Ap = 1
        orden.ocp_A1_Usu = user_id
        orden.ocp_A1_Dt = now_chile.date()
        orden.ocp_A1_Hr = now_chile.strftime("%H:%M:%S")

        db.commit()
        db.refresh(orden)

        self._eliminar_pdf_reppdf(loc_cod, ocp_nro, tenant_id)

        return orden

    def anular_orden(self, db: Session, ocp_nro: int, loc_cod: int) -> Optional[OrdenCompra]:
        """
        Anula una orden de compra seteando ocp_pdt = 'N'.
        """
        orden = db.query(OrdenCompra).filter(
            and_(
                OrdenCompra.ocp_nro == ocp_nro,
                OrdenCompra.Loc_cod == loc_cod,
                OrdenCompra.ocp_pdt != 'N'
            )
        ).first()

        if not orden:
            return None

        orden.ocp_pdt = 'N'
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

        orden.ocp_A1_Ap = 0
        orden.ocp_A1_Usu = ''
        orden.ocp_A1_Dt = date(1000, 1, 1)
        orden.ocp_A1_Hr = ''

        db.commit()
        db.refresh(orden)
        return orden
