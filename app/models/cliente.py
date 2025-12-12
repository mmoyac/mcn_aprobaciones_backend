"""
Modelo SQLAlchemy para tabla clientea (clientes del sistema)
"""
from sqlalchemy import Column, Integer, String, SmallInteger, Text, DECIMAL, BigInteger, Date
from app.db.base_class import Base


class Cliente(Base):
    """
    Modelo para clientes del sistema (clientea)
    """
    __tablename__ = "clientea"

    Cli_Code = Column(Integer, primary_key=True, comment="Código de cliente (RUT)")
    Cli_Name = Column(String(50), nullable=False, comment="Nombre del cliente")
    Cli_Digi = Column(String(1), nullable=False, comment="Dígito verificador")
    cli_gircod = Column(Integer, nullable=True, comment="Código de giro")
    Cli_NameL = Column(String(60), nullable=False, comment="Nombre largo")
    Ven_Cod = Column(SmallInteger, nullable=True, comment="Código vendedor")
    Cli_Sele = Column(String(1), nullable=False, comment="Cliente selección")
    Cli_Obs = Column(Text, nullable=False, comment="Observaciones")
    Cli_Dcto = Column(DECIMAL(4, 2), nullable=False, comment="Descuento")
    Cli_GirDs1 = Column(String(30), nullable=False, comment="Giro 1")
    Cli_GirDs2 = Column(String(30), nullable=False, comment="Giro 2")
    cli_blo = Column(SmallInteger, nullable=False, comment="Bloqueado")
    Cli_PagCod = Column(SmallInteger, nullable=False, comment="Código de pago")
    Cli_Est = Column(SmallInteger, nullable=False, comment="Estado")
    Cli_Cred = Column(BigInteger, nullable=False, comment="Crédito")
    Cli_Abo = Column(BigInteger, nullable=False, comment="Abono")
    Cli_Fe = Column(SmallInteger, nullable=False, comment="Factura electrónica")
    Cli_MailSII = Column(String(50), nullable=False, comment="Email SII")
    Cli_ExpoNro = Column(String(20), nullable=False, comment="Número exportación")

    def __repr__(self):
        return f"<Cliente(Cli_Code={self.Cli_Code}, Cli_Name={self.Cli_Name})>"
