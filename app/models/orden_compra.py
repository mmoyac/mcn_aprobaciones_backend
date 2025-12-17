from sqlalchemy import Column, Integer, String, Date, SmallInteger, BigInteger, ForeignKey, DECIMAL, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class OrdenCompra(Base):
    __tablename__ = "adq004"

    # Clave primaria compuesta
    Loc_cod = Column(SmallInteger, nullable=False)
    ocp_nro = Column(BigInteger, nullable=False)
    
    # Datos generales
    ocp_fec = Column(Date, nullable=False)
    ocp_fee = Column(Date, nullable=False) # Fecha entrega estimada?
    pro_rut = Column(Integer, ForeignKey("proveea.pro_rut"), nullable=False)
    
    # Detalle de montos
    ocp_net = Column(BigInteger, nullable=False)
    ocp_iva = Column(BigInteger, nullable=False)
    ocp_ila = Column(Integer, nullable=False) # Impuesto adicional?
    
    # Estados
    ocp_pdt = Column(String(1), nullable=False) # 'T' Recepcionada, 'I' Pendiente
    
    # Aprobación 1 (Liberación inicial)
    ocp_A1_Ap = Column(SmallInteger, nullable=False, default=0)
    ocp_A1_Usu = Column(String(10), nullable=False, default='')
    ocp_A1_Dt = Column(Date, nullable=False)
    ocp_A1_Hr = Column(String(8), nullable=False, default='')
    
    # Aprobación 2 (Aprobación final - equivalente a pre_vbgg)
    ocp_A2_Ap = Column(SmallInteger, nullable=False, default=0)
    ocp_A2_Usu = Column(String(10), nullable=False, default='')
    ocp_A2_Dt = Column(Date, nullable=False)
    ocp_A2_Hr = Column(String(8), nullable=False, default='')
    
    # Otros campos de aprobación
    ocp_A3_Anu = Column(SmallInteger, nullable=False, default=0)  # Anulación
    ocp_A3_Dt = Column(Date, nullable=False)
    ocp_A3_Hr = Column(String(8), nullable=False, default='')
    ocp_A3_Usu = Column(String(10), nullable=False, default='')
    
    ocp_A4_Ap = Column(SmallInteger, nullable=False, default=0)   # Aprobación nivel 4
    ocp_A4_Dt = Column(Date, nullable=False)
    ocp_A4_Hr = Column(String(8), nullable=False, default='')
    ocp_A4_Usu = Column(String(10), nullable=False, default='')

    # Relaciones
    proveedor = relationship("Proveedor", lazy="joined")

    __table_args__ = (
        PrimaryKeyConstraint('Loc_cod', 'ocp_nro'),
    )

    @property
    def proveedor_nombre(self):
        return self.proveedor.pro_nom if self.proveedor else "Desconocido"

    @property
    def monto_total(self):
        # Calculo solicitado: ocp_net + ocp_iva + ocp_ila
        return (self.ocp_net or 0) + (self.ocp_iva or 0) + (self.ocp_ila or 0)
