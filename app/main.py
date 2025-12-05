"""
FastAPI Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html

from app.core.config import get_settings
from app.api.v1.router import api_router

settings = get_settings()

app = FastAPI(
    title="MCN Aprobaciones Backend API",
    description="Backend API para sistema de aprobaciones de presupuestos",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None  # Deshabilitamos ReDoc por defecto para usar versión personalizada
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configurar según necesidades de seguridad
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers de API v1
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    """Endpoint raíz para verificar que la API está funcionando."""
    return {
        "message": "MCN Aprobaciones Backend API",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs",
        "api_v1": settings.API_V1_PREFIX
    }


@app.get("/health")
async def health_check():
    """Endpoint de health check."""
    return {"status": "healthy", "environment": settings.APP_ENV}


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    """
    Endpoint personalizado de ReDoc usando CDN alternativo.
    Evita problemas con tracking prevention.
    """
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="https://unpkg.com/redoc@latest/bundles/redoc.standalone.js",
    )
