# 🤖 AGENTS.md: Backend MCN APROBACIONES - Guía Operacional (FastAPI, SQLAlchemy, MySQL)

Este archivo sirve como el **manual de operaciones** y contexto esencial para cualquier agente de codificación o desarrollador.

El objetivo es mantener la consistencia en el entorno, el código y la arquitectura de la base de datos.

---

## 1. ⚙️ Arquitectura del Proyecto y Convenciones

### 1.1. Stack Tecnológico

| Componente | Tecnología | Rol |
| :--- | :--- | :--- |
| **Framework** | FastAPI (Python) | Capa de API REST. |
| **ORM** | SQLAlchemy (Core + ORM) | Mapeo objeto-relacional. |
| **Base de Datos** | MySQL (v5.7.7 - v5.7.23) | Almacenamiento persistente. |
| **Orquestación** | Docker Compose | Entorno de desarrollo aislado. |
| **CI/CD** | GitHub Actions | Automatización de tests y despliegue. |
| **Tests** | pytest + httpx | Suite de tests automatizados. |
| **Linting** | Black + Ruff | Calidad y formateo de código. |

### 1.2. Estructura del Directorio

El código fuente del backend (`mcn-aprobaciones-backend`) utiliza una arquitectura modular.

### 1.3. Convenciones de Codificación

* **Estilo:** PEP 8 (gestionado por herramientas de *linting* como Black o Ruff).
* **Nomenclatura:** Clases y *routers* en PascalCase. Funciones y variables en snake_case.
* **Gestión de Dependencias:** Se usa **`pip`** y el entorno virtual (`.venv`). El archivo **`requirements.txt`** es la única fuente de verdad para dependencias.

---

## 💾 Base de Datos

* **Servidor:** `179.27.210.204:3306`
* **Base de Datos:** Se usa una BD existente en MySQL con tablas ya creadas
* **Versión:** MySQL 5.7.7 - 5.7.23
* **Usuario:** lexasdulce
* **Database:** lexascl_mga

## 🔌 Puertos Críticos

| Entorno | Puerto | URL | Uso |
| :--- | :--- | :--- | :--- |
| **Desarrollo** | `8000` | http://localhost:8000 | Puerto libre en local |
| **Producción** | `8001` | https://api.lexastech.cl | Puerto 8000 ocupado por Portainer en VPS |

⚠️ **CRÍTICO:** En producción el puerto 8000 está ocupado por otro servicio. SIEMPRE usar puerto 8001 en `docker-compose.prod.yml`

## 3. 🐳 Configuración del Entorno

### 3.1. Desarrollo Local

Se requiere **Python 3.9+** y entorno virtual (`.venv`).

### 3.2. Arquitectura de Producción (VPS)

**Nginx Proxy Centralizado:** `/root/docker/nginx-proxy`
- Maneja puertos 80/443 para TODOS los dominios del VPS
- Certbot integrado con renovación automática
- Ver documentación: [`nginx-proxy/README.md`](nginx-proxy/README.md)

**MCN Backend:** `/root/docker/mcn`
- Solo contenedor backend (sin nginx propio)
- ⚠️ **Puerto mapeado:** `8001:8000` (puerto 8000 ocupado en VPS)
- Accesible externamente en `localhost:8001`
- Accesible internamente en `mcn_backend:8000`
- 🔥 **RED CRÍTICA:** `general-net` (externa, compartida con nginx_proxy)

### 🌐 Red general-net (CRÍTICO)

**Configuración obligatoria en producción:**
```yaml
networks:
  general-net:
    external: true
```

**Contenedores en general-net:**
- `nginx_proxy` (proxy reverso centralizado)
- `mcn_backend` (API backend)
- `mcn_postgres` (base de datos PDF)
- `mcn_frontend` (aplicación web)

⚠️ **FUNDAMENTAL:** Sin `general-net` el nginx_proxy NO puede comunicarse con los servicios backend

### 3.3. Variables de Entorno (`.env`)

El archivo **`.env`** en la raíz del proyecto es la fuente de configuración.

```bash
# Variables de MySQL
DB_USER=lexasdulce
DB_PASSWORD=Lexas1234
DB_NAME=lexascl_mga
DB_HOST=179.27.210.204
DB_PORT=3306

# Configuración de la aplicación
APP_ENV=development
DEBUG=True
API_V1_PREFIX=/api/v1

# Seguridad
SECRET_KEY=tu-clave-secreta-aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 2.3. Docker y Docker Compose

Para despliegue, se utiliza Docker:
- **Dockerfile**: Imagen base Python 3.11-slim con dependencias
- **docker-compose.yml**: Desarrollo local
- **docker-compose.prod.yml**: Producción (solo backend, proxy centralizado maneja SSL)
- **Health Check**: Verifica `/health` cada 30 segundos
- **Nginx Proxy**: `/root/docker/nginx-proxy` - Proxy reverso centralizado (80/443)

## 📁 Ubicación del DDL

Existe una carpeta **`schema/`** en la raíz del proyecto.

Para el acceso y desarrollo, la definición de las tablas está en `schema/db_tables.sql`

---

## 3. 🚢 Despliegue en Producción

### 3.1. Docker Hub

**Imagen Oficial:** `mmoyac/mcn_aprobaciones_backend:latest`

```bash
# Descargar y ejecutar
docker pull mmoyac/mcn_aprobaciones_backend:latest
docker run -d --name mcn_backend -p 8000:8000 --env-file .env mmoyac/mcn_aprobaciones_backend:latest
```

### 3.2. GitHub Actions - CI/CD Automático

El repositorio tiene dos workflows configurados:

#### Workflow 1: Tests (`.github/workflows/tests.yml`)
Se ejecuta en cada push y PR:
- Ejecuta pytest con cobertura
- Verifica linting con Ruff
- Verifica formateo con Black
- Sube reporte de cobertura a Codecov

#### Workflow 2: Docker Build & Push (`.github/workflows/docker-publish.yml`)
Se ejecuta manualmente (workflow_dispatch) o en tags de versión (v*):
- Construye imagen Docker
- Sube a Docker Hub automáticamente
- Despliega en VPS vía SSH
- Fuerza recreación del contenedor con `--force-recreate`
- Genera tags: `latest`, `v1.0.0`, `v1.1.0`, etc.

**Secrets requeridos en GitHub:**
- `DOCKER_USERNAME`: Usuario de Docker Hub
- `DOCKER_PASSWORD`: Access Token de Docker Hub
- `VPS_HOST`: IP del VPS (168.231.96.205)
- `VPS_USERNAME`: Usuario SSH (root)
- `VPS_SSH_KEY`: Clave privada SSH
- `VPS_PORT`: Puerto SSH (22)

**Para desplegar nueva versión:**
```bash
# Crear tag de versión
git tag -a v1.2.0 -m "Descripción de cambios"
git push origin v1.2.0

# O ejecutar manualmente desde GitHub Actions UI
# https://github.com/mmoyac/mcn_aprobaciones_backend/actions/workflows/docker-publish.yml
```

### 3.3. Migraciones Automáticas

Las migraciones se ejecutan automáticamente al iniciar el contenedor Docker (si se configuran en el entrypoint).

---

## 4. 📊 Endpoints Implementados

### 🔐 Autenticación (`/api/v1/auth`)

- **POST** `/login` - Autenticación con usuario y contraseña
  - Retorna token JWT válido por 30 minutos
  - Request: `{"usuario": "admin", "password": "123456"}`
  - Response: `{"access_token": "...", "token_type": "bearer", "usuario": "admin", "nombre": "Administrador"}`

### 👥 Usuarios (`/api/v1/usuarios`)

- **GET** `/` - Lista todos los usuarios con paginación (requiere auth)
- **GET** `/count` - Total de usuarios registrados (requiere auth)

**Nota:** La contraseña (UserLlave) NO se expone en ninguna respuesta.

### 📊 Presupuestos (`/api/v1/presupuestos`)

**Todos los endpoints requieren autenticación JWT en header:** `Authorization: Bearer <token>`

- **GET** `/indicadores` - Totales de presupuestos pendientes y aprobados
- **GET** `/pendientes` - Lista presupuestos pendientes (Pre_vbLib=1 AND pre_vbgg=0) **con campo `tienepdf`**
  - Incluye validación automática de existencia de PDF asociado
  - Campo `tienepdf`: 1 si existe PDF, 0 si no existe
- **GET** `/aprobados?usuario={user}&fecha_desde={date}&fecha_hasta={date}` - Presupuestos aprobados filtrados por usuario y rango de fechas
- **POST** `/aprobar` - Aprueba presupuesto (usuario se obtiene del token JWT)
  - Request: `{"Loc_cod": 1, "pre_nro": 12345}`
  - Valida que el usuario del token exista antes de aprobar
  - Actualiza: pre_vbgg=1, pre_vbggDt, pre_vbggTime, pre_vbggUsu

**Paginación:** Todos los endpoints de lista soportan `skip` y `limit` (max 1000)

**Integración PDF:** El endpoint `/pendientes` consulta automáticamente el servicio de documentos PDF para determinar si cada presupuesto tiene un PDF asociado, usando llamadas internas al endpoint `/api/v1/documentos-pdf/get`.

---

## 5. 🧪 Testing

**⚠️ IMPORTANTE: Los tests requieren contenedores Docker corriendo**

```bash
# 1. Iniciar contenedores (OBLIGATORIO)
docker-compose up -d --build --force-recreate

# 2. Verificar que estén corriendo
docker ps

# 3. Ejecutar tests
pytest

# Con cobertura
pytest --cov=app --cov-report=html

# Test específico (incluye integración PDF)
pytest tests/api/test_presupuestos.py -v
```

**Tests de Integración PDF:**
Los tests del endpoint `/presupuestos/pendientes` validan la integración completa:
- Autenticación JWT
- Consulta a base de datos MySQL
- Llamadas HTTP internas para validación de PDFs
- Campo `tienepdf` calculado dinámicamente
- Manejo de errores y timeouts

**Forzar Rebuild de Contenedores:**
```bash
# Rebuild completo sin cache (recomendado tras cambios)
docker-compose down --volumes --remove-orphans
docker-compose build --no-cache
docker-compose up -d
```

---

## 6. 🔧 Herramientas de Desarrollo

### Linting y Formateo

```bash
# Formatear código
black app/

# Verificar linting
ruff check app/

# Auto-fix linting
ruff check --fix app/
```

### Documentación Interactiva

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 7. 📚 Documentación

- **[README.md](README.md)** - Información general del proyecto
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Guía para colaboradores
- **[docs/API.md](docs/API.md)** - Documentación completa de endpoints
- **[docs/DOCKER.md](docs/DOCKER.md)** - Despliegue con Docker y CI/CD
- **[docs/CONFIGURACION_GITHUB_SECRETS.md](docs/CONFIGURACION_GITHUB_SECRETS.md)** - Configurar secrets en GitHub
- **[docs/PULL_REQUESTS.md](docs/PULL_REQUESTS.md)** - Flujo de trabajo con PRs
- **[docs/SETUP.md](docs/SETUP.md)** - Guía de instalación detallada
- **[docs/GIT.md](docs/GIT.md)** - Información del repositorio Git
- **[nginx-proxy/README.md](nginx-proxy/README.md)** - 🆕 Nginx proxy centralizado y gestión de dominios

---


## 8. 🔐 Seguridad

- **Autenticación por API Key (documentos PDF):** Todos los endpoints bajo `/api/v1/documentos-pdf/` requieren el header `x-api-key` con el valor configurado en la variable de entorno `API_KEY`.
    - Ejemplo de uso:
      ```http
      POST /api/v1/documentos-pdf/upsert HTTP/1.1
      Host: localhost:8000
      x-api-key: supersecreta123
      Content-Type: multipart/form-data
      ...
      ```

    - Solo los endpoints bajo `/api/v1/documentos-pdf/` (que usan PostgreSQL) requieren el header `x-api-key`.
    - El resto de los endpoints (usuarios, presupuestos, etc. - que usan MySQL) mantienen su autenticación JWT habitual.
    - Si la API key es incorrecta o falta, el endpoint responde 401 Unauthorized.
    - Cambia la clave en `.env` (`API_KEY`) para rotar el acceso sin modificar el código.

- **Autenticación JWT:** Todos los endpoints (excepto `/health` y `/auth/login`) requieren token JWT
- **Token Expiration:** 30 minutos (configurable en `.env` con `ACCESS_TOKEN_EXPIRE_MINUTES`)
- **Bearer Token:** Formato `Authorization: Bearer <token>` en headers
- No commitear archivos `.env` con credenciales reales
- Usar `.env.example` como plantilla sin valores sensibles
- Rotar `SECRET_KEY` en producción regularmente
- Usar Access Tokens de Docker Hub en lugar de contraseñas
- Configurar branch protection en GitHub (require PR approval)
- Las contraseñas de usuarios NO se exponen en respuestas API

---

## 6. 🧪 Testing y Base de Datos

### ⚠️ IMPORTANTE: Tests con Persistencia

**Los tests que utilizan la capa de persistencia DEBEN ejecutarse con contenedores Docker:**

```bash
# 1. OBLIGATORIO: Iniciar contenedores
docker-compose up -d

# 2. Verificar que estén corriendo
docker ps

# 3. Ejecutar tests con base de datos
pytest tests/api/test_documento_pdf.py  # PostgreSQL
pytest tests/api/test_presupuestos.py   # MySQL
pytest tests/api/test_usuarios.py       # MySQL
```

### ¿Por qué Contenedores para Tests?

- **PostgreSQL**: Endpoints `/documentos-pdf/*` necesitan host `postgres` (Docker) o `localhost:5432`
- **MySQL**: Otros endpoints necesitan conexión a base remota configurada
- **Configuración**: `conftest.py` configura `POSTGRES_HOST=localhost` para tests desde host
- **Integridad**: Tests validan persistencia real, no mocks

### Configuración de Test Environment

El archivo `conftest.py` configura automáticamente:
- `POSTGRES_HOST=localhost` (permite conexión host→container)  
- `API_KEY=supersecreta123` (autenticación para endpoints PDF)
- Variables de conexión PostgreSQL

---

## 7. 🐛 Troubleshooting Común

### Problemas de Puerto

**Desarrollo (Puerto 8000 en uso):**
```bash
# Windows PowerShell
Get-NetTCPConnection -LocalPort 8000 | Select-Object OwningProcess | Stop-Process -Force
```

**Producción (CRÍTICO - Configuración de puertos):**
- ✅ **docker-compose.yml** (desarrollo): Sin mapeo de puertos - usa puerto interno 8000
- ✅ **docker-compose.prod.yml** (producción): `ports: ["8001:8000"]` - OBLIGATORIO
- ❌ **Error común:** Usar puerto 8000 en producción (ocupado por Portainer)
- 🔧 **Solución:** Siempre verificar que docker-compose.prod.yml tenga el mapeo `8001:8000`

### Problemas con pydantic
```bash
# Reinstalar dependencias
pip uninstall -y pydantic pydantic-settings pydantic-core fastapi
pip install -r requirements.txt
```

### Conexión a MySQL falla
- Verificar que el servidor permite conexiones remotas
- Validar credenciales en `.env`
- Verificar firewall/puerto 3306

### API no responde (nginx 502/504)
- ✅ **Verificar red:** `docker network inspect general-net`
- ✅ **Contenedores en red:** nginx_proxy y mcn_backend deben estar en general-net
- ✅ **Conectividad interna:** `docker exec nginx_proxy wget -q -O - http://mcn_backend:8000/health`
- ✅ **Certificado SSL:** Verificar `/etc/letsencrypt/live/api.lexastech.cl/`
- ✅ **Recargar nginx:** `docker exec nginx_proxy nginx -s reload`

### ReDoc no carga (CDN bloqueado)
El proyecto usa `unpkg.com` en lugar de `jsdelivr` para evitar bloqueos de tracking prevention.

### Endpoint retorna 401 Unauthorized
- Verificar que el token JWT esté incluido en header `Authorization: Bearer <token>`
- Verificar que el token no haya expirado (30 minutos por defecto)
- Obtener nuevo token con POST `/api/v1/auth/login`

### Deploy no actualiza contenedor en VPS
- El workflow incluye `--force-recreate` para asegurar actualización
- Verificar que el tag de versión se creó correctamente
- Logs del workflow en: https://github.com/mmoyac/mcn_aprobaciones_backend/actions

---

**📌 Repositorio:** https://github.com/mmoyac/mcn_aprobaciones_backend
