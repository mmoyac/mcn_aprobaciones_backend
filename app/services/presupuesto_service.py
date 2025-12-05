"""
Servicio de lógica de negocio para presupuestos
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.models.presupuesto import Presupuesto
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
        - Pendientes: Pre_vbLib = 1 AND pre_vbgg = 0
          (Liberados pero pendientes de aprobación de gerencia)
        - Aprobados: pre_vbgg = 1
          (Aprobados por gerencia general)
        
        Args:
            db: Sesión de base de datos SQLAlchemy
            
        Returns:
            PresupuestoIndicadores: Objeto con contadores de pendientes y aprobados
            
        Example:
            >>> indicadores = PresupuestoService.obtener_indicadores(db)
            >>> print(f"Pendientes: {indicadores.pendientes}")
            >>> print(f"Aprobados: {indicadores.aprobados}")
        """
        
        # Contar presupuestos pendientes (liberados pero no aprobados)
        pendientes = db.query(func.count(Presupuesto.pre_nro)).filter(
            and_(
                Presupuesto.Pre_vbLib == 1,
                Presupuesto.pre_vbgg == 0
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
                Presupuesto.pre_vbgg == 0
            )
        ).order_by(
            Presupuesto.pre_fec.desc()
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def obtener_presupuestos_aprobados(
        db: Session,
        skip: int = 0,
        limit: int = 100
    ):
        """
        Obtiene listado de presupuestos aprobados.
        
        Args:
            db: Sesión de base de datos
            skip: Registros a omitir (para paginación)
            limit: Límite de registros a retornar
            
        Returns:
            List[Presupuesto]: Lista de presupuestos aprobados
        """
        return db.query(Presupuesto).filter(
            Presupuesto.pre_vbgg == 1
        ).order_by(
            Presupuesto.pre_vbggDt.desc()
        ).offset(skip).limit(limit).all()
