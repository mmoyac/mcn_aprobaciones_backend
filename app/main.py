"""
FastAPI Main Application
"""
from fastapi import FastAPI
from fastapi.responses import Response
from fastapi.openapi.docs import get_redoc_html
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest

from app.core.config import get_settings
from app.api.v1.router import api_router
from app.core.tenant_middleware import TenantMiddleware
from app.db.session_postgres import SessionPostgres
from app.models.tenant import Tenant
import os
from fastapi import Request, HTTPException, status

settings = get_settings()

app = FastAPI(
    title="MCN Aprobaciones Backend API",
    description="Backend API para sistema de aprobaciones de presupuestos",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None  # Deshabilitamos ReDoc por defecto para usar versión personalizada
)

# CORS dinámico: permite cualquier origen registrado en la tabla tenants
# Sin hardcodear dominios — agregar tenant en DB es suficiente.
class DynamicCORSMiddleware(BaseHTTPMiddleware):
    CORS_HEADERS = {
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
        "Access-Control-Allow-Headers": "Authorization, Content-Type, X-Tenant-Domain, X-API-Key",
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Max-Age": "600",
    }

    async def dispatch(self, request: StarletteRequest, call_next):
        origin = request.headers.get("origin", "")

        # Determinar si el origin está registrado como dominio de algún tenant
        allowed = False
        if origin:
            from urllib.parse import urlparse
            origin_host = urlparse(origin).hostname or ""
            db = SessionPostgres()
            try:
                tenant = db.query(Tenant).filter(
                    Tenant.dominio == origin_host,
                    Tenant.activo == True
                ).first()
                allowed = tenant is not None
            except Exception:
                pass
            finally:
                db.close()

        # Preflight OPTIONS — responder inmediatamente
        if request.method == "OPTIONS":
            headers = dict(self.CORS_HEADERS)
            if allowed and origin:
                headers["Access-Control-Allow-Origin"] = origin
            return Response(status_code=204, headers=headers)

        response = await call_next(request)

        if allowed and origin:
            response.headers["Access-Control-Allow-Origin"] = origin
            for k, v in self.CORS_HEADERS.items():
                response.headers[k] = v

        return response

app.add_middleware(DynamicCORSMiddleware)

# Middleware de resolución de tenant (debe ir ANTES del api_key_middleware)
app.add_middleware(TenantMiddleware)

# Incluir routers de API v1


# Middleware para validar API key en endpoints de documentos PDF
from fastapi.responses import JSONResponse
import sys
@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    # Solo proteger endpoints de documentos PDF (PostgreSQL)
    if request.url.path.startswith(f"{settings.API_V1_PREFIX}/documentos-pdf"):
        api_key = os.getenv("API_KEY")
        header_key = request.headers.get("x-api-key")
        if not api_key or header_key != api_key:
            return JSONResponse(status_code=401, content={"detail": f"Invalid or missing API Key. Path: {request.url.path}"})
    return await call_next(request)

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
