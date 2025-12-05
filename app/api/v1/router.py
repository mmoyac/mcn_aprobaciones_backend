"""
Router principal para API v1
"""
from fastapi import APIRouter
from app.api.v1.endpoints import presupuestos

api_router = APIRouter()

# Incluir routers de endpoints
api_router.include_router(
    presupuestos.router,
    prefix="/presupuestos",
    tags=["Presupuestos"]
)
