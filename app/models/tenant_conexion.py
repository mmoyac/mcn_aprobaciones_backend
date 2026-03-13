from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class TenantConexion(Base):
    __tablename__ = "tenant_conexiones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, unique=True)
    db_host = Column(String(200), nullable=False)
    db_port = Column(Integer, nullable=False, default=3306)
    db_name = Column(String(100), nullable=False)
    db_user = Column(String(100), nullable=False)
    db_password = Column(String(256), nullable=False)

    tenant = relationship("Tenant", back_populates="conexion")
