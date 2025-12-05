"""
Endpoints REST API para gestión de usuarios
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioDetalle
from app.services.usuario_service import UsuarioService

router = APIRouter()


@router.get(
    "/",
    response_model=List[UsuarioDetalle],
    summary="Listar todos los usuarios",
    description="""
    Retorna el listado completo de usuarios del sistema.
    
    **Nota:** La contraseña (UserLlave) NO se incluye en la respuesta por seguridad.
    
    Soporta paginación mediante parámetros skip y limit.
    """,
    tags=["Usuarios"]
)
async def listar_usuarios(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> List[UsuarioDetalle]:
    """
    Lista todos los usuarios del sistema con paginación.
    
    Args:
        skip: Número de registros a omitir (default: 0)
        limit: Cantidad máxima de registros a retornar (default: 100, max: 1000)
        db: Sesión de base de datos (inyectada automáticamente)
        
    Returns:
        List[UsuarioDetalle]: Lista de usuarios (sin contraseña)
        
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
        usuarios = UsuarioService.obtener_todos_usuarios(db, skip=skip, limit=limit)
        return usuarios
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener usuarios: {str(e)}"
        )


@router.get(
    "/count",
    response_model=dict,
    summary="Contar usuarios",
    description="Retorna el número total de usuarios registrados en el sistema.",
    tags=["Usuarios"]
)
async def contar_usuarios(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> dict:
    """
    Cuenta el total de usuarios en el sistema.
    
    Args:
        db: Sesión de base de datos (inyectada automáticamente)
        
    Returns:
        dict: {"total": número_de_usuarios}
        
    Raises:
        HTTPException: Error 500 si hay problemas con la base de datos
    """
    try:
        total = UsuarioService.contar_usuarios(db)
        return {"total": total}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al contar usuarios: {str(e)}"
        )
