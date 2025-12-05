# 🚀 Guía de Instalación y Configuración

## Requisitos Previos

- Python 3.9 o superior
- MySQL 5.7.7 - 5.7.23
- pip (gestor de paquetes de Python)
- Git (opcional, para clonar el repositorio)

---

## 📦 Instalación Paso a Paso

### 1. Clonar o Descargar el Proyecto

```bash
# Si usas Git
git clone https://github.com/mmoyac/mcn_aprobaciones_backend.git
cd mcn_aprobaciones_backend

# O descarga el ZIP y extráelo
```

### 2. Crear Entorno Virtual

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

### 3. Instalar Dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

Copia el archivo de ejemplo y configura tus credenciales:

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Edita el archivo `.env` con tus credenciales:

```env
# Variables de Base de Datos MySQL
DB_USER=lexasdulce
DB_PASSWORD=Lexas1234
DB_NAME=lexascl_mga
DB_HOST=179.27.210.204
DB_PORT=3306

# Configuración de la aplicación
APP_ENV=development
DEBUG=True
API_V1_PREFIX=/api/v1

# Seguridad - CAMBIAR EN PRODUCCIÓN
SECRET_KEY=tu-clave-secreta-super-segura-aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 5. Verificar Conexión a Base de Datos

Prueba la conexión ejecutando un script de verificación:

```python
# test_connection.py
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

```bash
python test_connection.py
```

---

## 🏃‍♂️ Ejecutar la Aplicación

### Modo Desarrollo (con auto-reload)

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Modo Producción

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Verificar que está funcionando

Abre tu navegador en:

- **API Root**: http://localhost:8000
- **Documentación Swagger**: http://localhost:8000/docs
- **Documentación ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## 🧪 Ejecutar Tests

```bash
# Ejecutar todos los tests
pytest

# Ejecutar con cobertura
pytest --cov=app tests/

# Ejecutar tests específicos
pytest tests/api/test_presupuestos.py

# Modo verbose
pytest -v
```

---

## 🐳 Alternativa: Docker (Opcional)

Si prefieres usar Docker para el desarrollo:

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - .:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Ejecutar con Docker:

```bash
docker-compose up --build
```

---

## 🔧 Comandos Útiles

### Actualizar Dependencias

```bash
pip list --outdated
pip install --upgrade package-name
pip freeze > requirements.txt
```

### Limpiar Cache de Python

```bash
# Windows
Get-ChildItem -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force
Get-ChildItem -Recurse -Filter "*.pyc" | Remove-Item -Force

# Linux/Mac
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type f -name "*.pyc" -delete
```

### Verificar Sintaxis y Estilo

```bash
# Formatear código con Black
black app/

# Linting con Ruff
ruff check app/

# Type checking (si se implementa)
mypy app/
```

---

## 📊 Verificar Endpoints

### Usando curl

```bash
# Obtener indicadores
curl http://localhost:8000/api/v1/presupuestos/indicadores

# Listar pendientes
curl http://localhost:8000/api/v1/presupuestos/pendientes?limit=5

# Listar aprobados
curl http://localhost:8000/api/v1/presupuestos/aprobados?limit=5
```

### Usando Python

```python
import requests

base_url = "http://localhost:8000/api/v1"

# Indicadores
response = requests.get(f"{base_url}/presupuestos/indicadores")
print(response.json())

# Pendientes
response = requests.get(f"{base_url}/presupuestos/pendientes", params={"limit": 10})
print(f"Total pendientes obtenidos: {len(response.json())}")
```

---

## ⚠️ Solución de Problemas

### Error: ModuleNotFoundError

```bash
# Asegúrate de que el entorno virtual está activado
# Reinstala las dependencias
pip install -r requirements.txt
```

### Error: Connection Refused (MySQL)

```bash
# Verifica que MySQL está corriendo
# Verifica credenciales en .env
# Verifica conectividad de red al servidor remoto
ping 179.27.210.204
```

### Error: Port 8000 already in use

```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8000
kill -9 <PID>
```

### Error: Import "app" could not be resolved

Esto es normal en algunos IDEs. Asegúrate de:
1. Tener el entorno virtual activado
2. Tener la raíz del proyecto como directorio de trabajo
3. Configurar el intérprete de Python en tu IDE apuntando a `.venv`

---

## 📝 Próximos Pasos

1. ✅ Instalación completada
2. ✅ Conexión a base de datos verificada
3. ✅ API funcionando
4. 🔜 Implementar autenticación
5. 🔜 Agregar más endpoints
6. 🔜 Implementar tests unitarios
7. 🔜 Deploy a producción

---

## 🆘 Soporte

Si encuentras problemas:

1. Revisa los logs de la aplicación
2. Verifica la configuración en `.env`
3. Consulta la documentación de FastAPI: https://fastapi.tiangolo.com
4. Revisa los logs de MySQL para problemas de conexión
