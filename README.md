# FME Backend - Sistema de Aprobaciones

Backend API desarrollado con FastAPI, SQLAlchemy y MySQL para el sistema de gestión de aprobaciones FME.

## 📋 Requisitos

- Python 3.9+
- MySQL 5.7.7 - 5.7.23
- pip

## 🚀 Instalación y Configuración

### 1. Clonar el repositorio

```bash
git clone https://github.com/mmoyac/mcn_aprobaciones_backend.git
cd mcn_aprobaciones_backend
```

### 2. Crear entorno virtual

```bash
python -m venv .venv
.venv\Scripts\activate  # En Windows
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Copiar el archivo `.env.example` a `.env` y configurar las variables:

```bash
copy .env.example .env
```

Editar `.env` con tus credenciales de base de datos.

### 5. Ejecutar la aplicación

```bash
uvicorn app.main:app --reload
```

La API estará disponible en: `http://localhost:8000`

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

```bash
pytest
```

## 📝 Documentación

La documentación interactiva de la API está disponible en:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🛠️ Stack Tecnológico

- **Framework**: FastAPI
- **ORM**: SQLAlchemy
- **Base de Datos**: MySQL
- **Testing**: pytest + httpx
- **Linting**: Black + Ruff

## 📄 Licencia

Este proyecto es privado y confidencial.
