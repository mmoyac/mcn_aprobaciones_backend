"""
Servicio de lógica de negocio para usuarios
"""
from sqlalchemy.orm import Session
from typing import List

from app.models.usuario import Usuario


class UsuarioService:
    """
    Servicio para gestión de usuarios del sistema
    """

    @staticmethod
    def obtener_todos_usuarios(db: Session, skip: int = 0, limit: int = 100) -> List[Usuario]:
        """
        Obtiene todos los usuarios del sistema con paginación
        
        Args:
            db: Sesión de base de datos
            skip: Registros a omitir (paginación)
            limit: Cantidad máxima de registros
            
        Returns:
            Lista de usuarios (sin contraseña)
        """
        return (
            db.query(Usuario)
            .order_by(Usuario.UserDs)  # Ordenar por nombre
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    @staticmethod
    def contar_usuarios(db: Session) -> int:
        """
        Cuenta el total de usuarios en el sistema
        
        Args:
            db: Sesión de base de datos
            
        Returns:
            Número total de usuarios
        """
        return db.query(Usuario).count()
