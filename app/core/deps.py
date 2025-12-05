"""
Dependencies para FastAPI - Autenticación y autorización
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.usuario import Usuario

# Esquema de seguridad Bearer Token
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Usuario:
    """
    Dependency que valida el token JWT y retorna el usuario actual.
    
    Este dependency debe ser usado en todos los endpoints protegidos.
    
    Args:
        credentials: Credenciales del header Authorization (Bearer token)
        db: Sesión de base de datos
        
    Returns:
        Usuario: Usuario autenticado
        
    Raises:
        HTTPException 401: Si el token es inválido o el usuario no existe
        
    Example:
        @router.get("/protected")
        async def protected_route(current_user: Usuario = Depends(get_current_user)):
            return {"user": current_user.UserCd}
    """
    token = credentials.credentials
    
    # Decodificar token
    usuario_id = decode_access_token(token)
    
    if usuario_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Buscar usuario en la base de datos
    usuario = db.query(Usuario).filter(Usuario.UserCd == usuario_id).first()
    
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return usuario


async def get_current_user_id(
    current_user: Usuario = Depends(get_current_user)
) -> str:
    """
    Dependency que retorna solo el ID del usuario actual.
    
    Útil cuando solo necesitas el UserCd sin todo el objeto Usuario.
    
    Args:
        current_user: Usuario actual (inyectado por get_current_user)
        
    Returns:
        str: UserCd del usuario autenticado
        
    Example:
        @router.post("/aprobar")
        async def aprobar(usuario: str = Depends(get_current_user_id)):
            # usuario contiene el UserCd
            pass
    """
    return current_user.UserCd
