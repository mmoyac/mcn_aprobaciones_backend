"""
Modelo SQLAlchemy para tabla ctbm01 (usuarios del sistema)
"""
from sqlalchemy import Column, String, SmallInteger
from app.db.base_class import Base


class Usuario(Base):
    """
    Modelo para usuarios del sistema (ctbm01)
    """
    __tablename__ = "ctbm01"

    UserCd = Column(String(10), primary_key=True, comment="Código de usuario")
    UserDs = Column(String(30), nullable=False, comment="Nombre del usuario")
    UserLlave = Column(String(6), nullable=False, comment="Contraseña")
    UserCta = Column(SmallInteger, nullable=False, comment="Permiso cuentas")
    UserParam = Column(SmallInteger, nullable=False, comment="Permiso parámetros")
    UserMaes = Column(SmallInteger, nullable=False, comment="Permiso maestros")
    UserMovi = Column(SmallInteger, nullable=False, comment="Permiso movimientos")
    UserUti = Column(SmallInteger, nullable=False, comment="Permiso utilidades")
    UserCon = Column(SmallInteger, nullable=False, comment="Permiso consultas")
    UserPerf = Column(SmallInteger, nullable=False, comment="Perfil de usuario")
    UserFolDte = Column(String(10), nullable=False, comment="Folio DTE")
    UserDte = Column(SmallInteger, nullable=False, comment="Permiso DTE")
    UserChPass = Column(String(1), nullable=False, comment="Cambio de contraseña")
    UserNameMail = Column(String(50), nullable=False, comment="Nombre para email")
    UserMail = Column(String(50), nullable=False, comment="Email")

