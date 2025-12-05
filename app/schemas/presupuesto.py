"""
Schemas Pydantic para presupuestos y sus indicadores
"""
from pydantic import BaseModel, Field
from datetime import date
from typing import Optional


class PresupuestoIndicadores(BaseModel):
    """
    Schema para los indicadores de presupuestos.
    
    Attributes:
        pendientes: Total de presupuestos pendientes de aprobación (Pre_vbLib=1 AND pre_vbgg=0)
        aprobados: Total de presupuestos aprobados (pre_vbgg=1)
    """
    
    pendientes: int = Field(
        ..., 
        description="Total de presupuestos pendientes de aprobación final",
        ge=0
    )
    aprobados: int = Field(
        ..., 
        description="Total de presupuestos aprobados por gerencia",
        ge=0
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "pendientes": 15,
                "aprobados": 234
            }
        }


class PresupuestoBase(BaseModel):
    """Schema base para presupuestos."""
    
    Loc_cod: int = Field(..., description="Código de local")
    pre_nro: int = Field(..., description="Número de presupuesto")
    pre_est: str = Field(..., description="Estado del presupuesto", max_length=1)
    pre_fec: date = Field(..., description="Fecha del presupuesto")
    pre_rut: int = Field(..., description="RUT del cliente")
    pre_VenCod: int = Field(..., description="Código del vendedor")
    Pre_Neto: int = Field(..., description="Monto neto del presupuesto")
    Pre_vbLib: int = Field(..., description="VB Liberación (1=aprobado)")
    pre_vbgg: int = Field(..., description="VB Gerencia (1=aprobado)")
    
    class Config:
        from_attributes = True


class PresupuestoDetalle(PresupuestoBase):
    """
    Schema con información detallada de un presupuesto.
    """
    
    pre_gl1: str = Field(..., description="Glosa línea 1")
    pre_fecAdj: date = Field(..., description="Fecha de adjudicación")
    pre_VbLibUsu: Optional[str] = Field(None, description="Usuario VB Liberación")
    Pre_VBLibDt: Optional[date] = Field(None, description="Fecha VB Liberación")
    pre_vbggUsu: Optional[str] = Field(None, description="Usuario VB Gerencia")
    pre_vbggDt: Optional[date] = Field(None, description="Fecha VB Gerencia")
    pre_trnFec: date = Field(..., description="Fecha de transacción")
    pre_trnusu: str = Field(..., description="Usuario de transacción")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "Loc_cod": 1,
                "pre_nro": 1234567,
                "pre_est": "A",
                "pre_fec": "2025-12-01",
                "pre_rut": 12345678,
                "pre_VenCod": 10,
                "Pre_Neto": 1500000,
                "Pre_vbLib": 1,
                "pre_vbgg": 0,
                "pre_gl1": "Presupuesto para proyecto X",
                "pre_fecAdj": "2025-12-05",
                "pre_VbLibUsu": "ADMIN",
                "Pre_VBLibDt": "2025-12-02",
                "pre_vbggUsu": "",
                "pre_vbggDt": None,
                "pre_trnFec": "2025-12-01",
                "pre_trnusu": "VENDEDOR1"
            }
        }
