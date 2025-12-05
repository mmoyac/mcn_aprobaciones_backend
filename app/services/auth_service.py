"""
Servicio de lógica de negocio para autenticación
"""
from sqlalchemy.orm import Session
from datetime import timedelta
from app.models.usuario import Usuario
from app.core.security import verify_password, create_access_token
from app.core.config import settings


class AuthService:
    """
    Servicio para operaciones de autenticación.
    """
    
    @staticmethod
    def autenticar_usuario(db: Session, usuario: str, password: str) -> dict:
        """
        Autentica un usuario verificando sus credenciales.
        
        Args:
            db: Sesión de base de datos
            usuario: Código de usuario (UserCd)
            password: Contraseña en texto plano
            
        Returns:
            dict: Datos del usuario autenticado con token JWT
            
        Raises:
            ValueError: Si las credenciales son inválidas
        """
        # Buscar usuario en la base de datos
        db_usuario = db.query(Usuario).filter(Usuario.UserCd == usuario).first()
        
        if not db_usuario:
            raise ValueError("Usuario o contraseña incorrectos")
        
        # Verificar contraseña
        # NOTA: En la BD la contraseña está en UserLlave
        # Por ahora verificamos directamente, pero idealmente debería estar hasheada
        if db_usuario.UserLlave != password:
            raise ValueError("Usuario o contraseña incorrectos")
        
        # Crear token JWT
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": db_usuario.UserCd},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "usuario": db_usuario.UserCd,
            "nombre": db_usuario.UserDs
        }
