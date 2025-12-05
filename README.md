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

## 🚀 Instalación Rápida

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

**🔗 La API estará disponible en:** http://localhost:8000

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
