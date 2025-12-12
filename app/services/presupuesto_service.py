"""
Servicio de lógica de negocio para presupuestos
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime
from app.models.presupuesto import Presupuesto
from app.models.usuario import Usuario
from app.schemas.presupuesto import PresupuestoIndicadores


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
    def obtener_presupuestos_pendientes(
        db: Session,
        skip: int = 0,
        limit: int = 100
    ):
        """
        Obtiene listado de presupuestos pendientes de aprobación.
        
        Args:
            db: Sesión de base de datos
            skip: Registros a omitir (para paginación)
            limit: Límite de registros a retornar
            
        Returns:
            List[Presupuesto]: Lista de presupuestos pendientes
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
        
        # Obtener fecha y hora actual
        ahora = datetime.now()
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