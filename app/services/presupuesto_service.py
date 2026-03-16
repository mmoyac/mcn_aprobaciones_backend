"""
Servicio de lógica de negocio para presupuestos
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, text
from datetime import datetime
import pytz
import os
from typing import List, Dict, Any
from app.models.presupuesto import Presupuesto
from app.models.usuario import Usuario
from app.schemas.presupuesto import PresupuestoIndicadores
from app.db.tenant_session import create_tenant_session


class PresupuestoService:
    """
    Servicio para operaciones de negocio relacionadas con presupuestos.
    
    Maneja la lógica de conteo y filtrado de presupuestos según
    sus estados de aprobación.
    """
    
    @staticmethod
    def obtener_indicadores(db: Session) -> PresupuestoIndicadores:
        """
        Obtiene los indicadores de presupuestos pendientes y aprobados.
        
        Lógica de negocio:
        - Pendientes: Pre_vbLib = 1 AND pre_vbgg = 0 y pre_est <> 'N'
          (Liberados pero pendientes de aprobación de gerencia y vigentes)
        - Aprobados: pre_vbgg = 1
          (Aprobados por gerencia general)
        
        Args:
            db: Sesión de base de datos SQLAlchemy
            
        Returns:
            PresupuestoIndicadores: Objeto con contadores de pendientes y aprobados
        """
        
        # Contar presupuestos pendientes (liberados pero no aprobados y vigentes)
        pendientes = db.query(func.count(Presupuesto.pre_nro)).filter(
            and_(
                Presupuesto.Pre_vbLib == 1,
                Presupuesto.pre_vbgg == 0,
                Presupuesto.pre_est != 'N'
            )
        ).scalar()
        
        # Contar presupuestos aprobados
        aprobados = db.query(func.count(Presupuesto.pre_nro)).filter(
            Presupuesto.pre_vbgg == 1
        ).scalar()
        
        return PresupuestoIndicadores(
            pendientes=pendientes or 0,
            aprobados=aprobados or 0
        )
    
    @staticmethod
    def _get_reppdf_session():
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

    @staticmethod
    def _verificar_pdfs_batch(items: list, tenant_id: int, tipo: int) -> dict:
        """
        Consulta en una sola query todos los PDFs para una lista de (loc_cod, numero).
        Retorna dict {(loc_cod, numero): estado} donde estado: 0=no existe, 1=con PDF, 2=sin contenido.
        """
        if not items:
            return {}
        db_cliente = PresupuestoService._get_reppdf_session()
        if not db_cliente:
            return {}
        try:
            # Construir lista de (loc_cod, numero) para la query
            pairs = [(loc_cod, numero) for loc_cod, numero in items]
            numeros = [p[1] for p in pairs]
            result = db_cliente.execute(
                text("""
                    SELECT PdfLocCod, PdfNumero, LENGTH(PdfBlob) as blob_size
                    FROM pdf001
                    WHERE PdfEmpCd = :emp_cd
                      AND PdfTipo   = :tipo
                      AND PdfNumero IN :numeros
                """),
                {"emp_cd": tenant_id, "tipo": tipo, "numeros": tuple(numeros)}
            )
            rows = result.fetchall()
            # Construir dict con resultado
            pdf_map = {}
            for row in rows:
                key = (row[0], row[1])  # (loc_cod, numero)
                blob_size = row[2] or 0
                pdf_map[key] = 1 if blob_size > 0 else 2
            # Los que no aparecieron = 0
            for loc_cod, numero in pairs:
                if (loc_cod, numero) not in pdf_map:
                    pdf_map[(loc_cod, numero)] = 0
            return pdf_map
        except Exception:
            return {}
        finally:
            db_cliente.close()

    @staticmethod
    def _verificar_pdf_existe(loc_cod: int, numero: int, tenant_id: int) -> int:
        """
        Verifica si existe PDF en la tabla pdf001 del cliente (lexascl_reppdf).
        Retorna: 0 = no existe, 1 = existe con PDF, 2 = existe sin PDF (blob vacío)
        """
        result = PresupuestoService._verificar_pdfs_batch([(loc_cod, numero)], tenant_id, 1)
        return result.get((loc_cod, numero), 0)

    @staticmethod
    def obtener_presupuestos_pendientes(
        db: Session,
        skip: int = 0,
        limit: int = 100
    ):
        """
        Obtiene listado de presupuestos pendientes de aprobación con indicador de PDF.
        
        Args:
            db: Sesión de base de datos
            skip: Registros a omitir (para paginación)
            limit: Límite de registros a retornar
            
        Returns:
            List[Presupuesto]: Lista de presupuestos pendientes (se agregará tienepdf en el endpoint)
        """
        return db.query(Presupuesto).filter(
            and_(
                Presupuesto.Pre_vbLib == 1,
                Presupuesto.pre_vbgg == 0,
                Presupuesto.pre_est != 'N'
            )
        ).order_by(
            Presupuesto.pre_fec.desc()
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def obtener_presupuestos_aprobados(
        db: Session,
        usuario: str,
        fecha_desde: str,
        fecha_hasta: str,
        skip: int = 0,
        limit: int = 100
    ):
        """
        Obtiene listado de presupuestos aprobados filtrados por usuario y rango de fechas.
        
        Args:
            db: Sesión de base de datos
            usuario: Código de usuario (pre_vbggUsu) que aprobó
            fecha_desde: Fecha inicial del rango (formato YYYY-MM-DD)
            fecha_hasta: Fecha final del rango (formato YYYY-MM-DD)
            skip: Registros a omitir (para paginación)
            limit: Límite de registros a retornar
            
        Returns:
            List[Presupuesto]: Lista de presupuestos aprobados por el usuario en el rango de fechas
        """
        return db.query(Presupuesto).filter(
            and_(
                Presupuesto.pre_vbgg == 1,
                Presupuesto.pre_vbggUsu == usuario,
                Presupuesto.pre_vbggDt >= fecha_desde,
                Presupuesto.pre_vbggDt <= fecha_hasta
            )
        ).order_by(
            Presupuesto.pre_vbggDt.desc()
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def aprobar_presupuesto(
        db: Session,
        loc_cod: int,
        pre_nro: int,
        usuario: str
    ) -> dict:
        """
        Aprueba un presupuesto actualizando sus campos de aprobación.
        
        Args:
            db: Sesión de base de datos
            loc_cod: Código de local
            pre_nro: Número de presupuesto
            usuario: Código del usuario que aprueba
            
        Returns:
            dict: Información del presupuesto aprobado
            
        Raises:
            ValueError: Si el presupuesto no existe o si el usuario no existe
        """
        # Validar que el usuario existe
        usuario_existe = db.query(Usuario).filter(Usuario.UserCd == usuario).first()
        if not usuario_existe:
            raise ValueError(f"Usuario no encontrado: {usuario}")
        
        # Buscar el presupuesto
        presupuesto = db.query(Presupuesto).filter(
            and_(
                Presupuesto.Loc_cod == loc_cod,
                Presupuesto.pre_nro == pre_nro
            )
        ).first()
        
        if not presupuesto:
            raise ValueError(f"Presupuesto no encontrado: Loc_cod={loc_cod}, pre_nro={pre_nro}")
        
        # Obtener fecha y hora actual en zona horaria de Chile
        chile_tz = pytz.timezone('America/Santiago')
        ahora = datetime.now(chile_tz)
        fecha_aprobacion = ahora.date()
        hora_aprobacion = ahora.strftime("%H:%M:%S")
        
        # Actualizar campos de aprobación
        presupuesto.pre_vbgg = 1
        presupuesto.pre_vbggUsu = usuario
        presupuesto.pre_vbggDt = fecha_aprobacion
        presupuesto.pre_vbggTime = hora_aprobacion
        
        # Guardar cambios
        db.commit()
        db.refresh(presupuesto)
        
        return {
            "Loc_cod": presupuesto.Loc_cod,
            "pre_nro": presupuesto.pre_nro,
            "pre_vbggUsu": presupuesto.pre_vbggUsu,
            "pre_vbggDt": presupuesto.pre_vbggDt,
            "pre_vbggTime": presupuesto.pre_vbggTime
        }

    @staticmethod
    def desaprobar_presupuesto(
        db: Session,
        loc_cod: int,
        pre_nro: int,
        usuario: str
    ) -> dict:
        """
        Desaprueba un presupuesto revirtiendo sus campos de aprobación.
        
        Args:
            db: Sesión de base de datos
            loc_cod: Código de local
            pre_nro: Número de presupuesto
            usuario: Código del usuario que realiza la acción
            
        Returns:
            dict: Información del presupuesto desaprobado
            
        Raises:
            ValueError: Si el presupuesto no existe o si el usuario no existe
        """
        # Validar que el usuario existe
        usuario_existe = db.query(Usuario).filter(Usuario.UserCd == usuario).first()
        if not usuario_existe:
            raise ValueError(f"Usuario no encontrado: {usuario}")
        
        # Buscar el presupuesto
        presupuesto = db.query(Presupuesto).filter(
            and_(
                Presupuesto.Loc_cod == loc_cod,
                Presupuesto.pre_nro == pre_nro
            )
        ).first()
        
        if not presupuesto:
            raise ValueError(f"Presupuesto no encontrado: Loc_cod={loc_cod}, pre_nro={pre_nro}")
        
        # Revertir campos de aprobación
        presupuesto.pre_vbgg = 0
        presupuesto.pre_vbggUsu = ''
        presupuesto.pre_vbggTime = ''
        
        # Para la fecha, al ser NOT NULL y date, debemos buscar un valor seguro.
        # Usaremos la fecha del presupuesto para mantener consistencia temporal mínima.
        presupuesto.pre_vbggDt = presupuesto.pre_fec
        
        # Guardar cambios
        db.commit()
        db.refresh(presupuesto)
        
        return {
            "Loc_cod": presupuesto.Loc_cod,
            "pre_nro": presupuesto.pre_nro,
            "pre_vbgg": presupuesto.pre_vbgg,
            "pre_vbggDt": presupuesto.pre_vbggDt,
            "pre_fec": presupuesto.pre_fec,
            "status": "desaprobado"
        }