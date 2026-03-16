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

        # Prioridad de resolución de dominio:
        # 1. X-Tenant-Domain (header explícito del frontend)
        # 2. Origin (enviado automáticamente por el browser en requests cross-origin)
        # 3. Referer (fallback adicional)
        # 4. Host (último recurso)
        x_tenant = request.headers.get("x-tenant-domain", "").strip().lower()
        origin = request.headers.get("origin", "").strip().lower()
        referer = request.headers.get("referer", "").strip().lower()

        if x_tenant:
            tenant_domain = x_tenant
        elif origin:
            # Origin tiene formato https://dominio.com — extraer solo el hostname
            from urllib.parse import urlparse
            tenant_domain = urlparse(origin).hostname or host
        elif referer:
            from urllib.parse import urlparse
            tenant_domain = urlparse(referer).hostname or host
        else:
            tenant_domain = host

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
