"""
Schemas Pydantic para usuarios
"""
from pydantic import BaseModel, Field


class UsuarioDetalle(BaseModel):
    """
    Schema para detalle de usuario (sin contraseña)
    """
    UserCd: str = Field(..., description="Código de usuario", max_length=10)
    UserDs: str = Field(..., description="Nombre del usuario", max_length=30)
    UserCta: int = Field(..., description="Permiso cuentas")
    UserParam: int = Field(..., description="Permiso parámetros")
    UserMaes: int = Field(..., description="Permiso maestros")
    UserMovi: int = Field(..., description="Permiso movimientos")
    UserUti: int = Field(..., description="Permiso utilidades")
    UserCon: int = Field(..., description="Permiso consultas")
    UserPerf: int = Field(..., description="Perfil de usuario")
    UserFolDte: str = Field(..., description="Folio DTE", max_length=10)
    UserDte: int = Field(..., description="Permiso DTE")
    UserChPass: str = Field(..., description="Cambio de contraseña", max_length=1)
    UserNameMail: str = Field(..., description="Nombre para email", max_length=50)
    UserMail: str = Field(..., description="Email", max_length=50)
    UserGAMGUID: str = Field(..., description="GUID GAM", max_length=40)

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "UserCd": "admin",
                "UserDs": "Administrador del Sistema",
                "UserCta": 1,
                "UserParam": 1,
                "UserMaes": 1,
                "UserMovi": 1,
                "UserUti": 1,
                "UserCon": 1,
                "UserPerf": 1,
                "UserFolDte": "001",
                "UserDte": 1,
                "UserChPass": "N",
                "UserNameMail": "Admin",
                "UserMail": "admin@ejemplo.com",
                "UserGAMGUID": ""
            }
        }
