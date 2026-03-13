from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.sql import func
from app.db.base_class import Base


class TenantTema(Base):
    __tablename__ = "tenant_temas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    color_primary = Column(String(7), nullable=False, server_default="#5EC8F2")
    color_secondary = Column(String(7), nullable=False, server_default="#45A29A")
    color_background = Column(String(7), nullable=False, server_default="#0F172A")
    color_surface = Column(String(7), nullable=False, server_default="#1E293B")
    color_text = Column(String(7), nullable=False, server_default="#F8FAFC")
    logo_url = Column(String(500), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
