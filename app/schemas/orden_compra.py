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
    tienepdf: Optional[int] = Field(None, description="0=no existe, 1=tiene PDF, 2=existe sin contenido", ge=0, le=2)
    loc_des: Optional[str] = None

    # Datos de aprobación (para la pestaña de aprobados)
    ocp_A2_Usu: Optional[str] = None
    ocp_A2_Dt: Optional[date] = None
    ocp_A2_Hr: Optional[str] = None

    class Config:
        from_attributes = True

# Esquema de aprobaciones para página de detalle
class AprobacionOrdenCompra(BaseModel):
    ocp_a4usu: Optional[str] = None
    ocp_a4_dt: Optional[date] = None
    ocp_a4_hr: Optional[str] = None
    ocp_a3usu: Optional[str] = None
    ocp_a3_dt: Optional[date] = None
    ocp_a3_hr: Optional[str] = None
    ocp_a2usu: Optional[str] = None
    ocp_a2_dt: Optional[date] = None
    ocp_a2_hr: Optional[str] = None
    ocp_a1usu: Optional[str] = None
    ocp_a1_dt: Optional[date] = None
    ocp_a1_hr: Optional[str] = None

class DetalleOrdenCompra(BaseModel):
    Loc_cod: int
    ocp_nro: int
    ocp_fec: Optional[date] = None
    ocp_fee: Optional[date] = None
    pro_rut: int
    proveedor_nombre: str
    ocp_pdt: str
    ocp_net: int
    ocp_iva: int
    ocp_ila: int
    monto_total: int
    loc_des: Optional[str] = None
    aprobaciones: AprobacionOrdenCompra = AprobacionOrdenCompra()

# Esquema para acción de aprobar/desaprobar
class OrdenCompraAprobar(BaseModel):
    Loc_cod: int
    ocp_nro: int

class OrdenCompraAprobadoResponse(BaseModel):
    message: str
    ocp_nro: int
    new_status: str

class ItemOrdenCompra(BaseModel):
    Loc_cod: int
    ocp_nro: int
    ocp_lin: int
    ocp_mat: Optional[str] = None
    mat_des: Optional[str] = None
    Ocp_Odt: Optional[int] = None
    Ocp_De1: Optional[str] = None
    Ocp_De2: Optional[str] = None
    Ocp_De3: Optional[str] = None
    Ocp_est: Optional[str] = None
    Ocp_can: Optional[float] = None
    Ocp_pre: Optional[int] = None
