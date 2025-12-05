"""
Endpoints REST API para autenticación
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import LoginRequest, LoginResponse
from app.services.auth_service import AuthService

router = APIRouter()


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Autenticar usuario",
    description="""
    Autentica un usuario con sus credenciales y retorna un token JWT.
    
    El token JWT debe ser incluido en el header Authorization de las siguientes requests:
    ```
    Authorization: Bearer <token>
    ```
    
    - **usuario**: Código de usuario (UserCd de la tabla ctbm01)
    - **password**: Contraseña del usuario (UserLlave)
    
    Retorna:
    - Token JWT de acceso
    - Datos básicos del usuario autenticado
    """,
    tags=["Autenticación"]
)
async def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
) -> LoginResponse:
    """
    Endpoint de login que autentica usuario y retorna token JWT.
    
    Args:
        credentials: Credenciales del usuario (usuario y password)
        db: Sesión de base de datos (inyectada automáticamente)
        
    Returns:
        LoginResponse: Token JWT y datos del usuario
        
    Raises:
        HTTPException 401: Si las credenciales son inválidas
        HTTPException 500: Si hay error en la base de datos
        
    Example:
        POST /api/v1/auth/login
        {
            "usuario": "admin",
            "password": "password123"
        }
    """
    try:
        resultado = AuthService.autenticar_usuario(
            db,
            usuario=credentials.usuario,
            password=credentials.password
        )
        
        return LoginResponse(**resultado)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al autenticar usuario: {str(e)}"
        )
