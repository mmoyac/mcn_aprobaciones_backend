"""
Router principal para API v1
"""
from fastapi import APIRouter
from app.api.v1.endpoints import presupuestos, usuarios, auth

api_router = APIRouter()

# Incluir routers de endpoints
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Autenticación"]
)

api_router.include_router(
    presupuestos.router,
    prefix="/presupuestos",
    tags=["Presupuestos"]
)

api_router.include_router(
    usuarios.router,
    prefix="/usuarios",
    tags=["Usuarios"]
)

from app.api.v1.endpoints import ordenes_compra

api_router.include_router(
    ordenes_compra.router,
    prefix="/ordenes-compra",
    tags=["Ordenes de Compra"]
)
