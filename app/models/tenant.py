from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, autoincrement=True)
    slug = Column(String(50), unique=True, nullable=False, index=True)
    nombre = Column(String(200), nullable=False)
    dominio = Column(String(200), unique=True, nullable=False, index=True)
    tema_id = Column(Integer, ForeignKey("tenant_temas.id"), nullable=False)
    activo = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    tema = relationship("TenantTema", lazy="joined")
    conexion = relationship("TenantConexion", back_populates="tenant", uselist=False, lazy="joined")
