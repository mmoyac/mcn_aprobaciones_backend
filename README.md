# MCN Backend - Sistema de Aprobaciones

Backend API desarrollado con FastAPI, SQLAlchemy y MySQL para el sistema de gestión de aprobaciones de presupuestos.

---

## 👥 ¿Nuevo Colaborador?

Si eres nuevo en este proyecto, **comienza aquí**:

### 📖 **[CONTRIBUTING.md](CONTRIBUTING.md)** - Guía Completa para Colaboradores

Esta guía incluye:
- ✅ Configuración inicial paso a paso
- ✅ Cómo ejecutar el proyecto localmente
- ✅ Flujo de trabajo con Git
- ✅ Solución de problemas comunes
- ✅ Buenas prácticas de desarrollo

---

## 📋 Requisitos

- Python 3.9+
- MySQL 5.7.7 - 5.7.23
- Git
- pip
- Docker (opcional, para despliegue)

## 🐳 Instalación con Docker (Recomendado)

```bash
# DESARROLLO - Puerto 8000 local
docker run -d \
  --name mcn_backend \
  -p 8000:8000 \
  -e DB_USER=tu_usuario \
  -e DB_PASSWORD=tu_password \
  mmoyac/mcn_aprobaciones_backend:latest

# PRODUCCIÓN - Puerto 8001 (8000 ocupado en VPS)
docker run -d \
  --name mcn_backend \
  -p 8001:8000 \
  -e DB_USER=tu_usuario \
  -e DB_PASSWORD=tu_password \
  mmoyac/mcn_aprobaciones_backend:latest

# Docker Compose (usa archivo correcto según entorno)
docker-compose up -d                    # Desarrollo
docker-compose -f docker-compose.prod.yml up -d  # Producción
```

⚠️ **IMPORTANTE**: En producción SIEMPRE usar puerto 8001 (el 8000 está ocupado por Portainer)

**📖 Documentación completa:** [docs/DOCKER.md](docs/DOCKER.md)

## 🚀 Instalación Manual

```bash
# 1. Clonar el repositorio
git clone https://github.com/mmoyac/mcn_aprobaciones_backend.git
cd mcn_aprobaciones_backend

# 2. Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac
# Edita .env con tus credenciales

# 5. Ejecutar el servidor
uvicorn app.main:app --reload
```

## 🔌 Configuración de Puertos

| Entorno | Puerto | URL | Docker Compose |
|---------|--------|-----|----------------|
| **Desarrollo** | `8000` | http://localhost:8000 | `docker-compose.yml` |
| **Producción** | `8001` | https://api.lexastech.cl | `docker-compose.prod.yml` |

⚠️ **CRÍTICO**: En el VPS de producción el puerto 8000 está ocupado por Portainer. SIEMPRE usar puerto 8001.

**🔗 URLs disponibles:**
- **Desarrollo:** http://localhost:8000
- **Producción:** https://api.lexastech.cl
- **Documentación:** /docs (Swagger UI)
- **Health Check:** /health

**📖 Para instrucciones detalladas, ver [CONTRIBUTING.md](CONTRIBUTING.md)**

## 📁 Estructura del Proyecto

```
mcn_aprobaciones_backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/      # Endpoints de la API
│   ├── core/                   # Configuración y seguridad
│   ├── db/                     # Configuración de base de datos
│   ├── models/                 # Modelos SQLAlchemy
│   ├── schemas/                # Esquemas Pydantic
│   ├── services/               # Lógica de negocio
│   ├── utils/                  # Utilidades
│   └── main.py                 # Aplicación principal
├── tests/                      # Tests automatizados
├── alembic/                    # Migraciones de base de datos
├── .env                        # Variables de entorno (no versionado)
├── requirements.txt            # Dependencias Python
└── README.md
```

## 🔗 Endpoints

- `GET /` - Información de la API
- `GET /health` - Health check
- `GET /docs` - Documentación interactiva (Swagger UI)
- `GET /redoc` - Documentación alternativa (ReDoc)

## 🧪 Tests

### Tests Básicos (sin persistencia)
```bash
# Ejecutar tests que no requieren base de datos
pytest tests/test_basic.py
```

### Tests con Base de Datos (requieren contenedores)
**⚠️ IMPORTANTE**: Los tests que utilizan PostgreSQL/MySQL requieren contenedores Docker ejecutándose.

```bash
# 1. Iniciar contenedores
docker-compose up -d --build --force-recreate

# 2. Verificar que PostgreSQL esté disponible
docker ps | grep postgres

# 3. Ejecutar tests con persistencia
pytest tests/api/test_documento_pdf.py
pytest tests/api/test_presupuestos.py -v

# 4. Ejecutar todos los tests
pytest

# Con cobertura
pytest --cov=app --cov-report=html
```

### ¿Por qué necesito contenedores para tests?
Los tests de endpoints que usan PostgreSQL (`/documentos-pdf/*`) y MySQL (otros endpoints) necesitan conectividad real a las bases de datos para validar:
- Creación y actualización de registros
- Consultas y filtros
- Integridad de datos
- Manejo de errores de persistencia
- **Integración PDF**: Tests de presupuestos validan automáticamente si existe PDF asociado via HTTP interno

## 📝 Documentación

La documentación interactiva de la API está disponible en:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 📚 Documentación Adicional

- **[API.md](docs/API.md)** - Documentación completa de endpoints
- **[DOCKER.md](docs/DOCKER.md)** - Despliegue con Docker y CI/CD
- **[CONFIGURACION_GITHUB_SECRETS.md](docs/CONFIGURACION_GITHUB_SECRETS.md)** - Configurar Docker Hub en GitHub Actions
- **[PULL_REQUESTS.md](docs/PULL_REQUESTS.md)** - Flujo de trabajo con PRs
- **[GIT.md](docs/GIT.md)** - Información del repositorio
- **[SETUP.md](docs/SETUP.md)** - Guía de instalación detallada

## 🛠️ Stack Tecnológico

- **Framework**: FastAPI
- **ORM**: SQLAlchemy
- **Base de Datos**: MySQL
- **Contenedores**: Docker + Docker Compose
- **CI/CD**: GitHub Actions
- **Testing**: pytest + httpx
- **Linting**: Black + Ruff

## 🚢 Despliegue

### Docker Hub

Imagen oficial: `mmoyac/mcn_aprobaciones_backend:latest`

```bash
docker pull mmoyac/mcn_aprobaciones_backend:latest
```

### GitHub Actions

El proyecto incluye workflows automáticos para:
- ✅ Tests automáticos en cada PR
- ✅ Linting y formateo de código
- ✅ Build y push a Docker Hub en cada push a `main`
- ✅ Generación de tags automáticos

**📖 Documentación:**
- **[docs/DOCKER.md](docs/DOCKER.md)** - Guía completa de despliegue con Docker
- **[docs/CONFIGURACION_GITHUB_SECRETS.md](docs/CONFIGURACION_GITHUB_SECRETS.md)** - Configurar secrets para Docker Hub

## 👥 Colaboración

Para contribuir al proyecto:

1. Lee la **[Guía para Colaboradores](CONTRIBUTING.md)**
2. Crea un fork del repositorio
3. Crea una rama para tu feature: `git checkout -b feature/AmazingFeature`
4. Commit tus cambios: `git commit -m 'Add: Amazing Feature'`
5. Push a la rama: `git push origin feature/AmazingFeature`
6. Abre un Pull Request

## 📞 Soporte

- 📖 **Documentación**: Carpeta `docs/`
- 🐛 **Issues**: [GitHub Issues](https://github.com/mmoyac/mcn_aprobaciones_backend/issues)
- 📧 **Contacto**: [GitHub Profile](https://github.com/mmoyac)

## 📄 Licencia

Este proyecto es privado y confidencial.
