from pydantic import BaseModel
from typing import Optional
from datetime import date

# Esquema para indicadores del dashboard
class OrdenCompraIndicadores(BaseModel):
    pendientes_count: int
    aprobados_hoy_count: int

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
    
    # Datos de aprobación (para la pestaña de aprobados)
    ocp_A1_Usu: Optional[str] = None
    ocp_A1_Dt: Optional[date] = None
    ocp_A1_Hr: Optional[str] = None

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
