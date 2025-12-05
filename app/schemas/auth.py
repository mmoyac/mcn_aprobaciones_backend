"""
Schemas Pydantic para autenticación
"""
from pydantic import BaseModel, Field
from typing import Optional


class LoginRequest(BaseModel):
    """
    Schema para solicitud de login.
    """
    usuario: str = Field(..., description="Código de usuario (UserCd)", max_length=10)
    password: str = Field(..., description="Contraseña del usuario")
    
    class Config:
        json_schema_extra = {
            "example": {
                "usuario": "admin",
                "password": "password123"
            }
        }


class Token(BaseModel):
    """
    Schema para respuesta de token JWT.
    """
    access_token: str = Field(..., description="Token JWT de acceso")
    token_type: str = Field(default="bearer", description="Tipo de token")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }


class TokenData(BaseModel):
    """
    Schema para datos extraídos del token JWT.
    """
    usuario: Optional[str] = None


class LoginResponse(BaseModel):
    """
    Schema para respuesta completa de login.
    """
    access_token: str = Field(..., description="Token JWT de acceso")
    token_type: str = Field(default="bearer", description="Tipo de token")
    usuario: str = Field(..., description="Código del usuario")
    nombre: str = Field(..., description="Nombre del usuario")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "usuario": "admin",
                "nombre": "Administrador"
            }
        }
