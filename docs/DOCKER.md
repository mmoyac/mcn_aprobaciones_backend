# 🐳 Despliegue con Docker

Esta guía explica cómo construir, ejecutar y desplegar la aplicación usando Docker y Docker Hub.

---

## 📋 Requisitos Previos

- **Docker** instalado ([Descargar](https://www.docker.com/products/docker-desktop))
- **Docker Compose** (incluido con Docker Desktop)
- Cuenta en **Docker Hub** ([Registrarse](https://hub.docker.com/signup))

---

## 🚀 Uso Rápido

### Ejecutar con Docker Compose

```bash
# 1. Configurar variables de entorno
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac
# Edita .env con tus credenciales

# 2. Iniciar los servicios
docker-compose up -d

# 3. Ver logs
docker-compose logs -f backend

# 4. Verificar que está funcionando
curl http://localhost:8000/health

# 5. Detener los servicios
docker-compose down
```

### Usar Imagen de Docker Hub

```bash
# Descargar y ejecutar la última versión
docker run -d \
  --name mcn_backend \
  -p 8000:8000 \
  -e DB_USER=tu_usuario \
  -e DB_PASSWORD=tu_password \
  -e DB_NAME=lexascl_mga \
  -e DB_HOST=179.27.210.204 \
  -e DB_PORT=3306 \
  -e SECRET_KEY=tu-secret-key \
  mmoyac/mcn_aprobaciones_backend:latest

# Ver logs
docker logs -f mcn_backend

# Detener
docker stop mcn_backend
docker rm mcn_backend
```

---

## 🏗️ Construcción de Imagen

### Construcción Local

```bash
# Construir la imagen
docker build -t mcn_aprobaciones_backend:local .

# Ejecutar la imagen local
docker run -d \
  --name mcn_backend_local \
  -p 8000:8000 \
  --env-file .env \
  mcn_aprobaciones_backend:local

# Ver logs
docker logs -f mcn_backend_local
```

### Construcción para Múltiples Plataformas

```bash
# Construir para AMD64 y ARM64
docker buildx create --use
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t mmoyac/mcn_aprobaciones_backend:latest \
  --push .
```

---

## 🔄 CI/CD con GitHub Actions

### Configuración Automática

El repositorio incluye dos workflows de GitHub Actions:

#### 1. **Tests Automáticos** (`.github/workflows/tests.yml`)

Se ejecuta en cada push y PR:
- ✅ Ejecuta linting con Ruff
- ✅ Verifica formateo con Black
- ✅ Ejecuta tests con pytest
- ✅ Genera reporte de cobertura

#### 2. **Build y Push a Docker Hub** (`.github/workflows/docker-publish.yml`)

Se ejecuta en cada push a `main` y en tags:
- ✅ Construye la imagen Docker
- ✅ Sube a Docker Hub automáticamente
- ✅ Genera tags automáticos (latest, versiones, SHA)

### Configurar Secrets en GitHub

Para que GitHub Actions funcione, debes configurar estos secrets:

1. Ve a tu repositorio en GitHub
2. **Settings** → **Secrets and variables** → **Actions**
3. Haz clic en **New repository secret**
4. Agrega estos secrets:

| Secret | Valor | Descripción |
|--------|-------|-------------|
| `DOCKER_USERNAME` | tu-usuario-dockerhub | Tu usuario de Docker Hub |
| `DOCKER_PASSWORD` | tu-token-dockerhub | Token de acceso de Docker Hub |

**⚠️ Importante:** Usa un **Access Token** en lugar de tu contraseña:
1. Ve a Docker Hub → Account Settings → Security
2. Haz clic en **New Access Token**
3. Copia el token generado
4. Úsalo como `DOCKER_PASSWORD`

### Tags Generados Automáticamente

GitHub Actions genera automáticamente estos tags:

- `latest` - Última versión de la rama main
- `main` - Última versión de la rama main
- `v1.0.0` - Cuando creas un tag de versión
- `pr-123` - Para Pull Requests
- `main-abc1234` - SHA del commit

---

## 📦 Publicar Manualmente a Docker Hub

### Paso 1: Login en Docker Hub

```bash
docker login
# Usuario: tu-usuario-dockerhub
# Password: tu-token-dockerhub
```

### Paso 2: Tag de la Imagen

```bash
# Tag con versión específica
docker tag mcn_aprobaciones_backend:local mmoyac/mcn_aprobaciones_backend:1.0.0

# Tag como latest
docker tag mcn_aprobaciones_backend:local mmoyac/mcn_aprobaciones_backend:latest
```

### Paso 3: Push a Docker Hub

```bash
# Subir versión específica
docker push mmoyac/mcn_aprobaciones_backend:1.0.0

# Subir latest
docker push mmoyac/mcn_aprobaciones_backend:latest
```

---

## 🔍 Comandos Útiles de Docker

### Gestión de Contenedores

```bash
# Ver contenedores corriendo
docker ps

# Ver todos los contenedores (incluyendo detenidos)
docker ps -a

# Ver logs en tiempo real
docker logs -f mcn_backend

# Entrar al contenedor
docker exec -it mcn_backend bash

# Ver uso de recursos
docker stats mcn_backend

# Reiniciar contenedor
docker restart mcn_backend

# Detener contenedor
docker stop mcn_backend

# Eliminar contenedor
docker rm mcn_backend
```

### Gestión de Imágenes

```bash
# Ver imágenes locales
docker images

# Eliminar imagen
docker rmi mmoyac/mcn_aprobaciones_backend:latest

# Actualizar imagen desde Docker Hub
docker pull mmoyac/mcn_aprobaciones_backend:latest

# Limpiar imágenes sin usar
docker image prune -a
```

### Docker Compose

```bash
# Iniciar servicios en background
docker-compose up -d

# Ver logs de todos los servicios
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f backend

# Reiniciar servicios
docker-compose restart

# Detener servicios
docker-compose stop

# Detener y eliminar contenedores
docker-compose down

# Detener, eliminar contenedores y volúmenes
docker-compose down -v

# Reconstruir imágenes
docker-compose build --no-cache

# Ver estado de servicios
docker-compose ps
```

---

## 🔧 Variables de Entorno

El contenedor acepta estas variables de entorno:

### Base de Datos (Requeridas)
```bash
DB_USER=lexasdulce
DB_PASSWORD=Lexas1234
DB_NAME=lexascl_mga
DB_HOST=179.27.210.204
DB_PORT=3306
```

### Aplicación
```bash
APP_ENV=production          # development, production
DEBUG=False                 # True, False
API_V1_PREFIX=/api/v1       # Prefijo de API
```

### Seguridad (Requeridas)
```bash
SECRET_KEY=tu-clave-secreta-aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## 🏥 Health Check

La imagen incluye un health check automático:

```bash
# Verificar health del contenedor
docker inspect --format='{{.State.Health.Status}}' mcn_backend

# Ver logs del health check
docker inspect --format='{{json .State.Health}}' mcn_backend | python -m json.tool
```

El health check verifica cada 30 segundos que el endpoint `/health` responde correctamente.

---

## 🌐 Despliegue en Producción

### Opción 1: Docker Compose en Servidor

```bash
# En el servidor de producción
git clone https://github.com/mmoyac/mcn_aprobaciones_backend.git
cd mcn_aprobaciones_backend

# Configurar variables de entorno
nano .env  # Editar con credenciales de producción

# Iniciar servicios
docker-compose up -d

# Verificar
curl http://localhost:8000/health
```

### Opción 2: Docker Run Directo

```bash
# En el servidor de producción
docker pull mmoyac/mcn_aprobaciones_backend:latest

docker run -d \
  --name mcn_backend \
  --restart unless-stopped \
  -p 8000:8000 \
  -e DB_USER=lexasdulce \
  -e DB_PASSWORD=Lexas1234 \
  -e DB_NAME=lexascl_mga \
  -e DB_HOST=179.27.210.204 \
  -e DB_PORT=3306 \
  -e APP_ENV=production \
  -e DEBUG=False \
  -e SECRET_KEY=tu-secret-key-de-produccion \
  -v /var/log/mcn_backend:/app/logs \
  mmoyac/mcn_aprobaciones_backend:latest
```

### Opción 3: Con Nginx Reverse Proxy

Archivo `nginx.conf`:

```nginx
server {
    listen 80;
    server_name api.tudominio.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 🐛 Troubleshooting

### Contenedor no inicia

```bash
# Ver logs detallados
docker logs mcn_backend

# Verificar variables de entorno
docker exec mcn_backend env | grep DB_

# Verificar conectividad a base de datos
docker exec mcn_backend ping -c 3 179.27.210.204
```

### Error de conexión a base de datos

```bash
# Verificar que las variables están configuradas
docker exec mcn_backend printenv | grep DB

# Probar conexión manualmente
docker exec -it mcn_backend python -c "
from app.core.config import get_settings
from app.db.session import engine
settings = get_settings()
print(f'Conectando a: {settings.DB_HOST}')
with engine.connect() as conn:
    print('Conexión exitosa!')
"
```

### Actualizar a nueva versión

```bash
# Detener contenedor actual
docker stop mcn_backend
docker rm mcn_backend

# Descargar nueva versión
docker pull mmoyac/mcn_aprobaciones_backend:latest

# Iniciar nuevo contenedor
docker run -d \
  --name mcn_backend \
  -p 8000:8000 \
  --env-file .env \
  mmoyac/mcn_aprobaciones_backend:latest
```

---

## 📊 Monitoreo

### Ver Uso de Recursos

```bash
# Uso en tiempo real
docker stats mcn_backend

# Información del contenedor
docker inspect mcn_backend
```

### Ver Logs

```bash
# Últimas 100 líneas
docker logs --tail 100 mcn_backend

# Logs en tiempo real
docker logs -f mcn_backend

# Logs con timestamps
docker logs -t mcn_backend
```

---

## 🔐 Seguridad

### Mejores Prácticas

1. **No usar contraseñas en código**
   - Siempre usar variables de entorno
   - Usar secrets de Docker o Kubernetes

2. **Actualizar imagen regularmente**
   ```bash
   docker pull mmoyac/mcn_aprobaciones_backend:latest
   ```

3. **Limitar recursos del contenedor**
   ```bash
   docker run -d \
     --name mcn_backend \
     --memory="512m" \
     --cpus="1.0" \
     -p 8000:8000 \
     mmoyac/mcn_aprobaciones_backend:latest
   ```

4. **Usar networks aislados**
   ```bash
   docker network create mcn_network
   ```

---

## 📚 Recursos Adicionales

- **Repositorio**: https://github.com/mmoyac/mcn_aprobaciones_backend
- **Docker Hub**: https://hub.docker.com/r/mmoyac/mcn_aprobaciones_backend
- **Documentación Docker**: https://docs.docker.com/
- **Docker Compose Docs**: https://docs.docker.com/compose/

---

**🎉 ¡Listo para desplegar!**

Con esta configuración, cada push a `main` desplegará automáticamente una nueva versión a Docker Hub.
