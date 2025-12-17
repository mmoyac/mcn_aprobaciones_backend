from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

# Esquema para indicadores del dashboard
class OrdenCompraIndicadores(BaseModel):
    total: int
    pendientes: int
    aprobadas: int

# Esquema base
class OrdenCompraBase(BaseModel):
    Loc_cod: int
    ocp_nro: int
    ocp_fec: date
    pro_rut: int
    ocp_pdt: str  # Estado ('I', 'T', etc.)
    
    # Montos
    ocp_net: int
    ocp_iva: int
    ocp_ila: int

# Esquema para detalle en listas (incluye datos calculados)
class OrdenCompraDetalle(OrdenCompraBase):
    ocp_fee: date
    proveedor_nombre: str
    monto_total: int
    tienepdf: Optional[int] = Field(None, description="Indica si tiene PDF asociado (0=No, 1=Sí)", ge=0, le=1)
    
    # Datos de aprobación (para la pestaña de aprobados)
    ocp_A2_Usu: Optional[str] = None
    ocp_A2_Dt: Optional[date] = None
    ocp_A2_Hr: Optional[str] = None

    class Config:
        from_attributes = True

# Esquema para acción de aprobar/desaprobar
class OrdenCompraAprobar(BaseModel):
    Loc_cod: int
    ocp_nro: int

class OrdenCompraAprobadoResponse(BaseModel):
    message: str
    ocp_nro: int
    new_status: str
