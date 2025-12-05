"""
Modelo SQLAlchemy para la tabla de presupuestos (cot013)
"""
from sqlalchemy import Column, BigInteger, SmallInteger, CHAR, Date, DECIMAL, Text
from app.db.session import Base


class Presupuesto(Base):
    """
    Modelo para la tabla cot013 (Presupuestos).
    
    Representa un presupuesto con toda su información asociada,
    incluyendo estados de aprobación y visto bueno.
    """
    
    __tablename__ = "cot013"
    
    # Clave primaria compuesta
    Loc_cod = Column(SmallInteger, primary_key=True, nullable=False)
    pre_nro = Column(BigInteger, primary_key=True, nullable=False)
    
    # Información básica del presupuesto
    pre_est = Column(CHAR(1), nullable=False, comment="Estado del presupuesto")
    pre_gl1 = Column(CHAR(40), nullable=False)
    pre_gl2 = Column(CHAR(40), nullable=False)
    pre_gl3 = Column(CHAR(40), nullable=False)
    pre_gl4 = Column(CHAR(40), nullable=False)
    pre_gl5 = Column(CHAR(40), nullable=False)
    pre_gl6 = Column(CHAR(40), nullable=False)
    pre_fecAdj = Column(Date, nullable=False, comment="Fecha de adjudicación")
    pre_fec = Column(Date, nullable=False, comment="Fecha del presupuesto")
    
    # Relaciones
    sol_nro = Column(BigInteger)
    pre_rut = Column(BigInteger, nullable=False, comment="RUT del cliente")
    pre_suc = Column(SmallInteger, nullable=False, comment="Sucursal del cliente")
    pre_VenCod = Column(SmallInteger, nullable=False, comment="Código del vendedor")
    
    # Detalles
    pre_req = Column(CHAR(20), nullable=False)
    pre_ate = Column(CHAR(20), nullable=False)
    pre_at1 = Column(CHAR(20), nullable=False)
    pre_ent = Column(CHAR(15), nullable=False)
    pre_entdd = Column(SmallInteger, nullable=False)
    pre_lug = Column(CHAR(20), nullable=False)
    ConPag_cod = Column(SmallInteger)
    
    # Observaciones
    pre_ob1 = Column(CHAR(70), nullable=False)
    pre_ob2 = Column(CHAR(70), nullable=False)
    pre_ob3 = Column(CHAR(70), nullable=False)
    pre_ob4 = Column(CHAR(70), nullable=False)
    pre_ob5 = Column(CHAR(70), nullable=False)
    pre_ob6 = Column(CHAR(70), nullable=False)
    pre_ob7 = Column(CHAR(70), nullable=False)
    pre_ob8 = Column(CHAR(70), nullable=False)
    pre_ob9 = Column(CHAR(70), nullable=False)
    pre_o10 = Column(CHAR(70), nullable=False)
    pre_o11 = Column(CHAR(70), nullable=False)
    pre_o12 = Column(CHAR(70), nullable=False)
    pre_o13 = Column(CHAR(70), nullable=False)
    pre_o14 = Column(CHAR(70), nullable=False)
    pre_o15 = Column(CHAR(70), nullable=False)
    pre_o16 = Column(CHAR(70), nullable=False)
    pre_o17 = Column(CHAR(70), nullable=False)
    pre_o18 = Column(CHAR(70), nullable=False)
    pre_o19 = Column(CHAR(70), nullable=False)
    pre_o20 = Column(CHAR(70), nullable=False)
    
    # Información adicional
    pre_pie = Column(CHAR(30), nullable=False)
    pre_tip = Column(CHAR(1), nullable=False, comment="Tipo de presupuesto")
    pre_tc = Column(DECIMAL(10, 2), nullable=False, comment="Tipo de cambio")
    pre_moncd = Column(SmallInteger, nullable=False, comment="Moneda")
    pre_ref = Column(Text, nullable=False)
    
    # Auditoría de transacción
    pre_trnFec = Column(Date, nullable=False, comment="Fecha de transacción")
    pre_trnhor = Column(CHAR(8), nullable=False, comment="Hora de transacción")
    pre_trnusu = Column(CHAR(10), nullable=False, comment="Usuario de transacción")
    
    # Garantía
    pre_gar = Column(SmallInteger, nullable=False, comment="Garantía")
    
    # Visto Bueno Liberación
    Pre_vbLib = Column(SmallInteger, nullable=False, comment="VB Liberación (1=aprobado)")
    Pre_VbLibUsu = Column(CHAR(10), nullable=False, comment="Usuario VB Liberación")
    Pre_VBLibDt = Column(Date, nullable=False, comment="Fecha VB Liberación")
    Pre_VbLibTime = Column(CHAR(8), nullable=False, comment="Hora VB Liberación")
    
    # Visto Bueno
    pre_vb = Column(SmallInteger, nullable=False, comment="Visto Bueno")
    pre_VbUsu = Column(CHAR(10), nullable=False, comment="Usuario VB")
    pre_VbFec = Column(Date, nullable=False, comment="Fecha VB")
    pre_VbTime = Column(CHAR(8), nullable=False, comment="Hora VB")
    
    # Visto Bueno Gerencia General (Aprobación final)
    pre_vbgg = Column(SmallInteger, nullable=False, comment="VB Gerencia (1=aprobado)")
    pre_vbggUsu = Column(CHAR(10), nullable=False, comment="Usuario VB Gerencia")
    pre_vbggDt = Column(Date, nullable=False, comment="Fecha VB Gerencia")
    pre_vbggTime = Column(CHAR(8), nullable=False, comment="Hora VB Gerencia")
    Pre_vbggAvi = Column(SmallInteger, nullable=False, comment="Aviso VB Gerencia")
    
    # Email
    Pre_MailEnv = Column(SmallInteger, nullable=False, comment="Mail enviado")
    Pre_Neto = Column(BigInteger, nullable=False, comment="Monto neto")
    Pre_MailUsu = Column(CHAR(10), nullable=False, comment="Usuario email")
    Pre_MailFec = Column(Date, nullable=False, comment="Fecha email")
    Pre_MailTime = Column(CHAR(8), nullable=False, comment="Hora email")
    Pre_MailSubjet = Column(Text, nullable=False, comment="Asunto email")
    Pre_MailPara = Column(Text, nullable=False, comment="Destinatarios email")
    
    def __repr__(self):
        return f"<Presupuesto(Loc_cod={self.Loc_cod}, pre_nro={self.pre_nro}, pre_est={self.pre_est})>"
