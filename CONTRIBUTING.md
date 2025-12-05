# 🚀 Guía Rápida para Colaboradores

Esta guía te ayudará a configurar el proyecto en tu máquina local para comenzar a desarrollar.

## 📋 Requisitos Previos

Asegúrate de tener instalado:

- **Python 3.9 o superior** ([Descargar](https://www.python.org/downloads/))
- **Git** ([Descargar](https://git-scm.com/downloads))
- **Acceso a la base de datos MySQL** (solicita credenciales al administrador)

---

## 🔧 Configuración Inicial (Primera vez)

### 1️⃣ Clonar el Repositorio

```bash
git clone https://github.com/mmoyac/mcn_aprobaciones_backend.git
cd mcn_aprobaciones_backend
```

### 2️⃣ Crear Entorno Virtual

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3️⃣ Instalar Dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4️⃣ Configurar Variables de Entorno

**Copia el archivo de ejemplo:**

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

**Edita el archivo `.env` con las credenciales correctas:**

```env
# Variables de Base de Datos MySQL
DB_USER=tu_usuario_mysql
DB_PASSWORD=tu_contraseña_mysql
DB_NAME=lexascl_mga
DB_HOST=179.27.210.204
DB_PORT=3306

# Configuración de la aplicación
APP_ENV=development
DEBUG=True
API_V1_PREFIX=/api/v1

# Seguridad - GENERA UNA CLAVE ÚNICA
SECRET_KEY=genera-una-clave-secreta-aqui-usando-secrets-token-urlsafe
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**💡 Para generar una SECRET_KEY segura:**

```python
# Ejecuta esto en una terminal de Python
import secrets
print(secrets.token_urlsafe(32))
```

### 5️⃣ Verificar Conexión a Base de Datos

Crea un archivo temporal `test_db.py`:

```python
from app.core.config import get_settings
from app.db.session import engine

settings = get_settings()
print(f"Conectando a: {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")

try:
    with engine.connect() as conn:
        print("✅ Conexión exitosa a MySQL!")
except Exception as e:
    print(f"❌ Error de conexión: {e}")
```

Ejecuta:
```bash
python test_db.py
```

Luego elimina el archivo.

---

## ▶️ Ejecutar el Proyecto

### Modo Desarrollo (con auto-reload)

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

El servidor estará disponible en:
- **API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### Modo Producción

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## 🧪 Ejecutar Tests

```bash
# Todos los tests
pytest

# Tests con cobertura
pytest --cov=app tests/

# Tests específicos
pytest tests/api/test_presupuestos.py

# Modo verbose
pytest -v
```

---

## 🌿 Flujo de Trabajo con Git

### ⚠️ IMPORTANTE: Solo Pull Requests

**Este repositorio tiene la rama `main` protegida.** No puedes hacer push directo. Debes trabajar con Pull Requests.

### Crear una Nueva Funcionalidad

```bash
# 1. Actualiza tu rama main
git checkout main
git pull origin main

# 2. Crea una nueva rama (OBLIGATORIO)
git checkout -b feature/nombre-de-tu-funcionalidad
# Ejemplos de nombres de rama:
# - feature/endpoint-eliminar-presupuestos
# - fix/correccion-validacion-fechas
# - docs/actualizar-readme

# 3. Realiza tus cambios y haz commits
git add .
git commit -m "Add: Descripción clara de tus cambios"

# 4. Sube tu rama (NO A MAIN)
git push origin feature/nombre-de-tu-funcionalidad

# 5. Crea un Pull Request en GitHub
# Ve a: https://github.com/mmoyac/mcn_aprobaciones_backend
# GitHub te mostrará un botón "Compare & pull request"
# Llena la plantilla del PR con toda la información
# Espera la aprobación del administrador
```

**📖 Para más detalles sobre Pull Requests, ver [docs/PULL_REQUESTS.md](docs/PULL_REQUESTS.md)**

### Buenas Prácticas para Commits

```bash
# ✅ Buenos mensajes de commit
git commit -m "Add: Endpoint para eliminar presupuestos"
git commit -m "Fix: Corrección en validación de fechas"
git commit -m "Update: Mejora en performance de queries"
git commit -m "Docs: Actualización de README"

# ❌ Evitar mensajes vagos
git commit -m "cambios"
git commit -m "fix"
git commit -m "update"
```

---

## 📁 Estructura del Proyecto

```
mcn_aprobaciones_backend/
├── app/
│   ├── api/v1/endpoints/    # Endpoints REST
│   ├── core/                # Configuración
│   ├── db/                  # Conexión a BD
│   ├── models/              # Modelos SQLAlchemy
│   ├── schemas/             # Schemas Pydantic
│   ├── services/            # Lógica de negocio
│   ├── utils/               # Utilidades
│   └── main.py              # App principal
├── tests/                   # Tests
├── docs/                    # Documentación
├── schema/                  # DDL de base de datos
├── .env                     # Variables de entorno (NO SUBIR)
├── .env.example             # Plantilla de variables
├── requirements.txt         # Dependencias
└── README.md               # Documentación principal
```

---

## 🔍 Comandos Útiles

### Formateo de Código

```bash
# Formatear con Black
black app/

# Verificar estilo con Ruff
ruff check app/

# Auto-fix con Ruff
ruff check --fix app/
```

### Ver Logs de Base de Datos

Si necesitas ver las queries SQL, edita `app/core/config.py` y asegúrate de que `DEBUG=True`.

### Actualizar Dependencias

```bash
# Ver dependencias desactualizadas
pip list --outdated

# Actualizar una específica
pip install --upgrade nombre-paquete

# Actualizar requirements.txt
pip freeze > requirements.txt
```

---

## 🐛 Solución de Problemas Comunes

### Error: ModuleNotFoundError

```bash
# Asegúrate de que el entorno virtual está activado
# Reinstala las dependencias
pip install -r requirements.txt
```

### Error: Connection Refused (MySQL)

```bash
# Verifica credenciales en .env
# Verifica conectividad de red
ping 179.27.210.204

# Verifica que el puerto no esté bloqueado
```

### Error: Port already in use

```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8000
kill -9 <PID>
```

### Error: Import "app" could not be resolved

Esto es un problema de configuración del IDE. En VS Code:
1. Presiona `Ctrl+Shift+P`
2. Busca "Python: Select Interpreter"
3. Selecciona el intérprete de `.venv`

---

## 📚 Recursos Adicionales

- **Documentación API**: Ver `docs/API.md`
- **Guía de Setup**: Ver `docs/SETUP.md`
- **Estado del Proyecto**: Ver `docs/ESTADO_PROYECTO.md`
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org

---

## 🆘 Obtener Ayuda

Si tienes problemas:

1. Revisa la documentación en la carpeta `docs/`
2. Busca en los [Issues de GitHub](https://github.com/mmoyac/mcn_aprobaciones_backend/issues)
3. Crea un nuevo Issue describiendo el problema
4. Contacta al administrador del proyecto

---

## ✅ Checklist de Inicio

Antes de comenzar a desarrollar, verifica que:

- [ ] Python 3.9+ instalado
- [ ] Repositorio clonado
- [ ] Entorno virtual creado y activado
- [ ] Dependencias instaladas
- [ ] Archivo `.env` configurado con credenciales correctas
- [ ] Conexión a base de datos verificada
- [ ] Servidor funcionando en http://localhost:8000
- [ ] Tests ejecutándose correctamente

---

**¡Listo para desarrollar! 🎉**

Si completaste todos los pasos, ya puedes comenzar a trabajar en el proyecto.
