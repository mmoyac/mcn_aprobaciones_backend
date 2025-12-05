# 🔐 Configuración de GitHub Secrets para Docker Hub

Esta guía te mostrará cómo configurar los secrets necesarios en GitHub para que las GitHub Actions puedan subir automáticamente las imágenes Docker a Docker Hub.

---

## 📋 Requisitos Previos

1. **Cuenta de Docker Hub** - Si no tienes una, regístrate en https://hub.docker.com/signup
2. **Acceso de Administrador** al repositorio de GitHub
3. **Tu usuario de Docker Hub** (ejemplo: `mmoyac`)

---

## 🔑 Paso 1: Crear Access Token en Docker Hub

**⚠️ IMPORTANTE:** No uses tu contraseña de Docker Hub directamente. Usa un Access Token.

### 1.1. Ingresar a Docker Hub

1. Ve a https://hub.docker.com/
2. Inicia sesión con tu cuenta

### 1.2. Crear el Access Token

1. Haz clic en tu **nombre de usuario** (esquina superior derecha)
2. Selecciona **Account Settings**
3. En el menú lateral, haz clic en **Security**
4. Busca la sección **Access Tokens**
5. Haz clic en **New Access Token**

### 1.3. Configurar el Token

- **Access Token Description:** `GitHub Actions - MCN Backend` (o el nombre que prefieras)
- **Access permissions:** Selecciona **Read, Write, Delete** (para poder subir imágenes)
- Haz clic en **Generate**

### 1.4. Guardar el Token

**⚠️ MUY IMPORTANTE:**
- Copia el token inmediatamente (solo se muestra una vez)
- Guárdalo en un lugar seguro temporalmente
- Si pierdes el token, deberás crear uno nuevo

Ejemplo de token: `dckr_pat_abc123XYZ...`

---

## 🔧 Paso 2: Configurar Secrets en GitHub

### 2.1. Acceder a la Configuración del Repositorio

1. Ve a tu repositorio en GitHub: https://github.com/mmoyac/mcn_aprobaciones_backend
2. Haz clic en **Settings** (⚙️)
3. En el menú lateral izquierdo, busca la sección **Security**
4. Haz clic en **Secrets and variables** → **Actions**

### 2.2. Agregar el Secret DOCKER_USERNAME

1. Haz clic en **New repository secret**
2. Configura:
   - **Name:** `DOCKER_USERNAME`
   - **Value:** Tu usuario de Docker Hub (ejemplo: `mmoyac`)
3. Haz clic en **Add secret**

### 2.3. Agregar el Secret DOCKER_PASSWORD

1. Haz clic en **New repository secret** nuevamente
2. Configura:
   - **Name:** `DOCKER_PASSWORD`
   - **Value:** El token que copiaste en el Paso 1.4
3. Haz clic en **Add secret**

### 2.4. Verificar los Secrets

Deberías ver ambos secrets listados:
- ✅ `DOCKER_USERNAME`
- ✅ `DOCKER_PASSWORD`

**Nota:** Por seguridad, no podrás ver el valor de los secrets después de crearlos.

---

## ✅ Paso 3: Verificar que Funciona

### 3.1. Trigger Manual (Opcional)

Si quieres probar inmediatamente sin hacer un push:

1. Ve a **Actions** en tu repositorio
2. Selecciona el workflow **"Build and Push to Docker Hub"**
3. Haz clic en **Run workflow**
4. Selecciona la rama `main`
5. Haz clic en **Run workflow**

### 3.2. Push Automático

El workflow se ejecutará automáticamente cuando:
- Hagas push a la rama `main`
- Crees un Pull Request
- Crees un tag de versión (ej: `v1.0.0`)

### 3.3. Ver el Progreso

1. Ve a la pestaña **Actions** en tu repositorio
2. Verás el workflow ejecutándose
3. Haz clic en el workflow para ver los detalles
4. Espera a que termine (puede tomar 2-5 minutos)

### 3.4. Verificar en Docker Hub

1. Ve a https://hub.docker.com/
2. Navega a tu repositorio: https://hub.docker.com/r/mmoyac/mcn_aprobaciones_backend
3. Deberías ver la nueva imagen con el tag `latest` y otros tags generados

---

## 🏷️ Tags Generados Automáticamente

GitHub Actions genera estos tags para cada build:

| Evento | Tag Generado | Ejemplo |
|--------|--------------|---------|
| Push a `main` | `latest`, `main`, `main-SHA` | `latest`, `main`, `main-be53bb2` |
| Pull Request | `pr-NUMBER` | `pr-42` |
| Tag de versión | `vX.Y.Z`, `X.Y` | `v1.0.0`, `1.0` |
| Branch específico | `branch-name` | `develop` |

---

## 🔄 Actualizar o Rotar Token

Si necesitas cambiar el token:

1. Crea un nuevo token en Docker Hub (Paso 1)
2. Ve a GitHub → Settings → Secrets and variables → Actions
3. Haz clic en `DOCKER_PASSWORD`
4. Haz clic en **Update secret**
5. Pega el nuevo token
6. Haz clic en **Update secret**

---

## 🐛 Troubleshooting

### Error: "Invalid username or password"

**Causa:** Token incorrecto o expirado

**Solución:**
1. Verifica que `DOCKER_USERNAME` sea tu usuario exacto de Docker Hub
2. Crea un nuevo token en Docker Hub
3. Actualiza `DOCKER_PASSWORD` con el nuevo token

### Error: "denied: requested access to the resource is denied"

**Causa:** El usuario no tiene permisos de escritura en el repositorio de Docker Hub

**Solución:**
1. Verifica que el repositorio `mmoyac/mcn_aprobaciones_backend` existe en Docker Hub
2. Verifica que el token tenga permisos de **Write**
3. Si el repositorio no existe, Docker Hub lo creará automáticamente la primera vez

### El workflow se ejecuta pero no sube la imagen

**Causa:** Los secrets no están configurados correctamente

**Solución:**
1. Ve a Settings → Secrets and variables → Actions
2. Verifica que ambos secrets existen:
   - `DOCKER_USERNAME`
   - `DOCKER_PASSWORD`
3. Actualiza los valores si es necesario

### Ver logs de error

1. Ve a Actions → Selecciona el workflow fallido
2. Haz clic en el job **"build-and-push"**
3. Expande el paso **"Log in to Docker Hub"** para ver el error

---

## 📚 Recursos Adicionales

- **Docker Hub Security:** https://docs.docker.com/docker-hub/access-tokens/
- **GitHub Secrets:** https://docs.github.com/en/actions/security-guides/encrypted-secrets
- **Docker Build Push Action:** https://github.com/docker/build-push-action

---

## ✅ Checklist de Verificación

Antes de hacer push, verifica:

- [ ] Tienes una cuenta de Docker Hub
- [ ] Creaste un Access Token en Docker Hub
- [ ] Configuraste `DOCKER_USERNAME` en GitHub Secrets
- [ ] Configuraste `DOCKER_PASSWORD` con el token en GitHub Secrets
- [ ] El workflow está en `.github/workflows/docker-publish.yml`
- [ ] El Dockerfile está en la raíz del proyecto

**🎉 ¡Listo! Ahora cada push a `main` desplegará automáticamente a Docker Hub.**
