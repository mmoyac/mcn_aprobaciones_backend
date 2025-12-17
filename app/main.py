"""
FastAPI Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html

from app.core.config import get_settings
from app.api.v1.router import api_router
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

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configurar según necesidades de seguridad
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


@app.get("/db-test")
async def db_test():
    """Endpoint temporal para probar conexión a BD."""
    from sqlalchemy import text
    from app.db.session import SessionLocal
    import traceback
    
    try:
        db = SessionLocal()
        # Intentar una consulta simple
        result = db.execute(text("SELECT 1")).scalar()
        return {
            "status": "success",
            "result": result,
            "connection_info": {
                "host": settings.DB_HOST,
                "user": settings.DB_USER,
                "db": settings.DB_NAME
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc()
        }
    finally:
        if 'db' in locals():
            db.close()


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
