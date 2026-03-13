"""
Middleware de resolución de tenant.
Lee el header Host de cada request, busca el tenant en PostgreSQL
y lo adjunta a request.state.tenant para uso en endpoints y dependencias.
"""
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.db.session_postgres import SessionPostgres
from app.models.tenant import Tenant

# Rutas que no requieren resolución de tenant
_BYPASS_PATHS = {"/", "/health", "/docs", "/redoc", "/openapi.json", "/db-test"}


class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Siempre adjuntar tenant al estado (None si no se encuentra)
        request.state.tenant = None

        path = request.url.path
        if path in _BYPASS_PATHS or path.startswith("/docs") or path.startswith("/openapi"):
            return await call_next(request)

        # Extraer host limpio (sin puerto)
        host = request.headers.get("host", "").split(":")[0].lower()

        # X-Tenant-Domain tiene prioridad (útil en producción donde el API
        # está en un dominio distinto al del frontend, ej: api.lexastech.cl)
        tenant_domain = request.headers.get("x-tenant-domain", "").strip().lower() or host

        if tenant_domain:
            db = SessionPostgres()
            try:
                tenant = db.query(Tenant).filter(
                    Tenant.dominio == tenant_domain,
                    Tenant.activo == True
                ).first()
                request.state.tenant = tenant
            except Exception:
                # Si la tabla aún no existe (ej: primera migración), no bloquear
                pass
            finally:
                db.close()

        return await call_next(request)
