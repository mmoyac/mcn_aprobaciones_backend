
"""
Router principal para API v1
"""
from fastapi import APIRouter
from app.api.v1.endpoints import presupuestos, usuarios, auth, documento_pdf, ordenes_compra

api_router = APIRouter()

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
api_router.include_router(
    ordenes_compra.router,
    prefix="/ordenes-compra",
    tags=["Ordenes de Compra"]
)
api_router.include_router(
    documento_pdf.router,
    prefix="/documentos-pdf",
    tags=["Documentos PDF"]
)
