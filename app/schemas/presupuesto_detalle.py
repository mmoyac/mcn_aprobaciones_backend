"""
Schemas Pydantic para el detalle de presupuesto (items cot005 y costos cot005l)
y búsqueda histórica
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import date


class CostoItem(BaseModel):
    pre_lin: int
    pre_dtlin: int
    Pre_DtTip: int
    tipo_nombre: str
    Pre_DtCant: float
    Pre_DtPre: float
    Pre_DtDescrip: Optional[str] = ""


class ItemPresupuesto(BaseModel):
    pre_lin: int
    pre_des: Optional[str] = ""
    pre_de1: Optional[str] = ""
    pre_de2: Optional[str] = ""
    pre_de3: Optional[str] = ""
    pre_de4: Optional[str] = ""
    pre_cpr: float
    pre_pre: float
    pre_dct: float
    costos: List[CostoItem] = []


class DetallePresupuesto(BaseModel):
    loc_cod: int
    pre_nro: int
    items: List[ItemPresupuesto] = []


class PresupuestoHistorico(BaseModel):
    Loc_cod: int
    pre_nro: int
    pre_fec: Optional[date] = None
    pre_rut: Optional[int] = None
    cliente_nombre: Optional[str] = ""
    sol_nro: Optional[int] = None
    pre_ref: Optional[str] = ""
    Pre_Neto: Optional[int] = 0
    pre_est: Optional[str] = ""
    pre_vbgg: Optional[int] = 0
    pre_vbggUsu: Optional[str] = ""
    pre_vbggDt: Optional[date] = None
    tienepdf: Optional[int] = 0
