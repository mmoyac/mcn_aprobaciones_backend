from sqlalchemy import Column, Integer, String, SmallInteger, BigInteger
from app.db.base_class import Base

class Proveedor(Base):
    __tablename__ = "proveea"

    pro_rut = Column(Integer, primary_key=True, index=True)
    pro_nom = Column(String(40), nullable=False)
    # Otros campos existen en la tabla pero solo necesitamos estos por ahora
    # para el join con OrdenCompra
