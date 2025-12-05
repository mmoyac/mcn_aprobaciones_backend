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
- Accesible internamente en `mcn_backend:8000`
- Conectado a red `general-net`

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
Se ejecuta en push a `main` y en tags:
- Construye imagen Docker
- Sube a Docker Hub automáticamente
- Genera tags: `latest`, `main`, `v1.0.0`, `pr-123`, `main-abc1234`

**Secrets requeridos en GitHub:**
- `DOCKER_USERNAME`: Usuario de Docker Hub
- `DOCKER_PASSWORD`: Access Token de Docker Hub

### 3.3. Migraciones Automáticas

Las migraciones se ejecutan automáticamente al iniciar el contenedor Docker (si se configuran en el entrypoint).

---

## 4. 📊 Endpoints Implementados

### Presupuestos (`/api/v1/presupuestos`)

- **GET** `/indicadores` - Totales de presupuestos pendientes y aprobados
- **GET** `/pendientes` - Lista presupuestos pendientes (Pre_vbLib=1 AND pre_vbgg=0)
- **GET** `/aprobados` - Lista presupuestos aprobados (pre_vbgg=1)

**Paginación:** Todos los endpoints de lista soportan `skip` y `limit` (max 1000)

---

## 5. 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Con cobertura
pytest --cov=app --cov-report=html

# Test específico
pytest tests/api/test_presupuestos.py
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

- No commitear archivos `.env` con credenciales reales
- Usar `.env.example` como plantilla sin valores sensibles
- Rotar `SECRET_KEY` en producción
- Usar Access Tokens de Docker Hub en lugar de contraseñas
- Configurar branch protection en GitHub (require PR approval)

---

## 9. 🐛 Troubleshooting Común

### Puerto 8000 en uso
```bash
# Windows PowerShell
Get-NetTCPConnection -LocalPort 8000 | Select-Object OwningProcess | Stop-Process -Force
```

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

### ReDoc no carga (CDN bloqueado)
El proyecto usa `unpkg.com` en lugar de `jsdelivr` para evitar bloqueos de tracking prevention.

---

**📌 Repositorio:** https://github.com/mmoyac/mcn_aprobaciones_backend
