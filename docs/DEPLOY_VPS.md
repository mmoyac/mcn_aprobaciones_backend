# 🚀 Despliegue Automático a VPS

Esta guía explica cómo configurar el despliegue automático desde GitHub Actions a tu VPS.

---

## 📋 Información del VPS

- **IP:** 168.231.96.205
- **Usuario:** root
- **Directorio de trabajo:** /root/docker/mcn
- **Puerto SSH:** 22 (default)
- **Puerto HTTP:** 80
- **Puerto HTTPS:** 443

---

## 🔐 Paso 1: Generar SSH Key en el VPS

### 1.1. Conectarse al VPS

```bash
ssh root@168.231.96.205
```

### 1.2. Crear directorio de trabajo

```bash
mkdir -p /root/docker/mcn
cd /root/docker/mcn
```

### 1.3. Generar par de llaves SSH para GitHub Actions

```bash
# Generar llave SSH dedicada para GitHub Actions
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github_actions_deploy
```

**Importante:** NO pongas contraseña (presiona Enter cuando te lo pida)

### 1.4. Agregar la llave pública al authorized_keys

```bash
cat ~/.ssh/github_actions_deploy.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### 1.5. Obtener la llave PRIVADA (para GitHub Secrets)

```bash
cat ~/.ssh/github_actions_deploy
```

**⚠️ COPIA TODO EL CONTENIDO** (desde `-----BEGIN OPENSSH PRIVATE KEY-----` hasta `-----END OPENSSH PRIVATE KEY-----`)

---

## 🔧 Paso 2: Configurar Secrets en GitHub

### 2.1. Ir a GitHub Secrets

1. Ve a: https://github.com/mmoyac/mcn_aprobaciones_backend/settings/secrets/actions
2. Haz clic en **New repository secret**

### 2.2. Agregar VPS_HOST

- **Name:** `VPS_HOST`
- **Value:** `168.231.96.205`
- Click en **Add secret**

### 2.3. Agregar VPS_USERNAME

- **Name:** `VPS_USERNAME`
- **Value:** `root`
- Click en **Add secret**

### 2.4. Agregar VPS_SSH_KEY

- **Name:** `VPS_SSH_KEY`
- **Value:** Pega la llave privada que copiaste (todo el contenido incluyendo las líneas `-----BEGIN` y `-----END`)
- Click en **Add secret**

### 2.5. Agregar VPS_PORT (opcional)

- **Name:** `VPS_PORT`
- **Value:** `22`
- Click en **Add secret**

---

## 📦 Paso 3: Preparar el VPS para Docker

### 3.1. Instalar Docker (si no está instalado)

```bash
# Actualizar sistema
apt update && apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Verificar instalación
docker --version
```

### 3.2. Crear archivo .env en el VPS

```bash
cd /root/docker/mcn
nano .env
```

**Contenido del .env:**

```bash
# Variables de Base de Datos MySQL
DB_USER=lexasdulce
DB_PASSWORD=Lexas1234
DB_NAME=lexascl_mga
DB_HOST=179.27.210.204
DB_PORT=3306

# Configuración de la aplicación
APP_ENV=production
DEBUG=False
API_V1_PREFIX=/api/v1

# Seguridad
SECRET_KEY=tu-clave-secreta-de-produccion-super-segura
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Guardar:** Ctrl+O, Enter, Ctrl+X

### 3.3. Crear docker-compose.yml en el VPS (Opcional)

```bash
cd /root/docker/mcn
nano docker-compose.yml
```

**Contenido:**

```yaml
version: '3.8'

services:
  backend:
    image: mmoyac/mcn_aprobaciones_backend:latest
    container_name: mcn_backend
    restart: unless-stopped
    ports:
    ports:
      - "80:80"
      - "443:443"
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

**Guardar:** Ctrl+O, Enter, Ctrl+X

---

## ✅ Paso 4: Verificar Configuración

### 4.1. Probar conexión SSH desde GitHub

Después de configurar los secrets, puedes probar manualmente:

```bash
# En tu máquina local (PowerShell)
ssh -i ruta/a/llave root@168.231.96.205
```

### 4.2. Verificar que Docker funciona

```bash
# En el VPS
docker ps
docker pull mmoyac/mcn_aprobaciones_backend:latest
curl http://localhost/health
# o
curl https://api.lexastech.cl/health
```

---

## 🚀 Paso 5: Ejecutar el Despliegue

### Opción A: Manual desde GitHub Actions

1. Ve a: https://github.com/mmoyac/mcn_aprobaciones_backend/actions/workflows/docker-publish.yml
2. Click en **Run workflow**
3. Selecciona rama `main`
4. Click en **Run workflow**

### Opción B: Crear una versión

```bash
git tag v1.0.0 -m "Primera version en produccion"
git push origin v1.0.0
```

---

## 🔍 Verificar el Despliegue

### En el VPS:

```bash
# Ver contenedores corriendo
docker ps

# Ver logs del contenedor
docker logs -f mcn_backend

# Verificar que responde
curl http://localhost/health
```

### Desde Internet:

```bash
# Verificar endpoint público
curl https://api.lexastech.cl/health
```

**📖 Documentación API:** https://api.lexastech.cl/docs

---

## 🔒 Seguridad Adicional

### Recomendaciones:

1. **Firewall:** Asegúrate de que los puertos 80, 443 y 22 (SSH) estén abiertos
   ```bash
   ufw allow 22
   ufw allow 80
   ufw allow 443
   ufw enable
   ```

2. **Nginx Reverse Proxy:** Considera usar Nginx con SSL
   ```bash
   apt install nginx certbot python3-certbot-nginx
   ```

3. **Cambiar SECRET_KEY:** Usa una clave segura en producción
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

---

## 🐛 Troubleshooting

### Error: "Permission denied (publickey)"

**Solución:**
```bash
# En el VPS, verificar permisos
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
chmod 600 ~/.ssh/github_actions_deploy
```

### Error: "Connection refused"

**Solución:**
```bash
# Verificar que SSH está corriendo
systemctl status ssh
systemctl start ssh
```

### El contenedor no inicia

**Solución:**
```bash
# Ver logs detallados
docker logs mcn_backend

# Verificar variables de entorno
docker exec mcn_backend env | grep DB_
```

---

## 📚 Comandos Útiles

```bash
# Ver logs en tiempo real
docker logs -f mcn_backend

# Reiniciar contenedor
docker restart mcn_backend

# Actualizar a última versión
docker pull mmoyac/mcn_aprobaciones_backend:latest
docker-compose up -d --force-recreate

# Ver uso de recursos
docker stats mcn_backend

# Entrar al contenedor
docker exec -it mcn_backend bash
```

---

**✅ Una vez completados estos pasos, cada despliegue será automático!**
