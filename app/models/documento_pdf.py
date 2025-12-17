from sqlalchemy import Column, BigInteger, SmallInteger, TIMESTAMP, LargeBinary
from sqlalchemy.sql import func
from app.db.base_class import Base

class DocumentoPDF(Base):
    __tablename__ = "documentos_pdf"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    tipo = Column(SmallInteger, nullable=False, comment="1=presupuesto, 2=orden de compra")
    numero = Column(BigInteger, nullable=False)
    fecha_creacion = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    pdf = Column(LargeBinary, nullable=False)
