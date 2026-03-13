"""
Dependencies para FastAPI - Autenticación y autorización
"""
from typing import Generator
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.tenant_session import create_tenant_session
from app.models.usuario import Usuario

# Esquema de seguridad Bearer Token
security = HTTPBearer()


def get_tenant_db(request: Request) -> Generator[Session, None, None]:
    """
    Dependency que retorna una sesión SQLAlchemy a la BD MySQL del tenant actual.
    El tenant es resuelto por TenantMiddleware a partir del header Host.
    """
    tenant = getattr(request.state, "tenant", None)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant no encontrado para este dominio"
        )
    if not tenant.conexion:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El tenant no tiene base de datos configurada"
        )
    conn = tenant.conexion
    db = create_tenant_session(conn.db_host, conn.db_port, conn.db_name, conn.db_user, conn.db_password)
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_tenant_db)
) -> Usuario:
    """
    Dependency que valida el token JWT y retorna el usuario actual.
    """
    token = credentials.credentials

    usuario_id = decode_access_token(token)

    if usuario_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"}
        )

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
    """
    return current_user.UserCd

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


def get_tenant_db(request: Request) -> Generator[Session, None, None]:
    """
    Dependency que retorna una sesión SQLAlchemy a la BD MySQL del tenant actual.
    El tenant es resuelto por TenantMiddleware a partir del header Host.

    Uso:
        @router.get("/datos")
        def endpoint(db: Session = Depends(get_tenant_db)):
            ...

    Raises:
        HTTPException 404: Si no hay tenant para el dominio o sin conexión configurada.
    """
    tenant = getattr(request.state, "tenant", None)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant no encontrado para este dominio"
        )
    if not tenant.conexion:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El tenant no tiene base de datos configurada"
        )
    conn = tenant.conexion
    db = create_tenant_session(conn.db_host, conn.db_port, conn.db_name, conn.db_user, conn.db_password)
    try:
        yield db
    finally:
        db.close()
