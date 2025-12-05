# 🔒 Configuración de Protección de Ramas y Pull Requests

Esta guía explica cómo configurar el repositorio para que los colaboradores trabajen mediante Pull Requests que requieren aprobación.

---

## 📋 Guía Rápida para Colaboradores

### Si NO eres colaborador directo (Fork):
```bash
# 1. Hacer fork en GitHub.com
# 2. Clonar TU fork
git clone https://github.com/tu-usuario/mcn_aprobaciones_backend.git
cd mcn_aprobaciones_backend

# 3. Configurar upstream
git remote add upstream https://github.com/mmoyac/mcn_aprobaciones_backend.git

# 4. Crear rama
git checkout -b feature/mi-feature

# 5. Hacer cambios, commit y push a TU fork
git add .
git commit -m "Add: Mi cambio"
git push origin feature/mi-feature

# 6. Crear PR desde tu fork en GitHub.com
```

### Si ERES colaborador directo (Rama):
```bash
# 1. Clonar el repositorio original
git clone https://github.com/mmoyac/mcn_aprobaciones_backend.git
cd mcn_aprobaciones_backend

# 2. Crear rama
git checkout -b feature/mi-feature

# 3. Hacer cambios, commit y push
git add .
git commit -m "Add: Mi cambio"
git push origin feature/mi-feature

# 4. Crear PR en GitHub.com
```

**📖 Instrucciones detalladas abajo ↓**

---

## 🎯 Objetivo

- Los colaboradores pueden hacer fork o trabajar en ramas
- Solo pueden integrar cambios mediante Pull Requests
- Los Pull Requests requieren tu aprobación antes de fusionarse
- La rama `main` está protegida contra pushes directos

---

## ⚙️ Configuración en GitHub (Para el Administrador)

### 1️⃣ Proteger la Rama Main

1. Ve a tu repositorio en GitHub:
   **https://github.com/mmoyac/mcn_aprobaciones_backend**

2. Haz clic en **Settings** (Configuración)

3. En el menú lateral, haz clic en **Branches**

4. En "Branch protection rules", haz clic en **Add rule**

5. Configura lo siguiente:

   **Branch name pattern:**
   ```
   main
   ```

   **Activa estas opciones:**
   
   ✅ **Require a pull request before merging**
   - ✅ Require approvals: **1** (o más si prefieres)
   - ✅ Dismiss stale pull request approvals when new commits are pushed
   - ✅ Require review from Code Owners (opcional)
   
   ✅ **Require status checks to pass before merging** (si tienes CI/CD)
   - ✅ Require branches to be up to date before merging
   
   ✅ **Require conversation resolution before merging** (recomendado)
   
   ✅ **Include administrators** (opcional - también te aplica a ti las reglas)
   
   ✅ **Restrict who can push to matching branches** (opcional - más restrictivo)
   - Agrega solo tu usuario aquí

6. Haz clic en **Create** o **Save changes**

---

## 👥 Flujo de Trabajo para Colaboradores

### Opción A: Fork del Repositorio (Colaboradores Externos)

**Ideal para:** Personas que NO son colaboradores directos del repositorio.

#### Paso 1: Hacer Fork en GitHub

1. Ve a: **https://github.com/mmoyac/mcn_aprobaciones_backend**
2. Haz clic en el botón **Fork** (arriba a la derecha)
3. Selecciona tu cuenta personal
4. Espera a que GitHub cree tu fork (copia del repositorio)

#### Paso 2: Clonar TU Fork (no el original)

```bash
# Clona TU fork (reemplaza 'tu-usuario' con tu nombre de usuario de GitHub)
git clone https://github.com/tu-usuario/mcn_aprobaciones_backend.git
cd mcn_aprobaciones_backend
```

#### Paso 3: Configurar el Repositorio Original como "Upstream"

Esto te permite mantener tu fork actualizado con el repositorio original:

```bash
# Agregar el repo original como upstream
git remote add upstream https://github.com/mmoyac/mcn_aprobaciones_backend.git

# Verificar que se agregó correctamente
git remote -v
# Deberías ver:
# origin    https://github.com/tu-usuario/mcn_aprobaciones_backend.git (fetch)
# origin    https://github.com/tu-usuario/mcn_aprobaciones_backend.git (push)
# upstream  https://github.com/mmoyac/mcn_aprobaciones_backend.git (fetch)
# upstream  https://github.com/mmoyac/mcn_aprobaciones_backend.git (push)
```

#### Paso 4: Configurar Variables de Entorno

```bash
# Copia el archivo de ejemplo
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac

# Edita el .env con las credenciales (solicítalas al administrador)
```

#### Paso 5: Instalar Dependencias

```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
.\.venv\Scripts\Activate.ps1  # Windows PowerShell
# .venv\Scripts\activate.bat   # Windows CMD
# source .venv/bin/activate    # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt
```

#### Paso 6: Crear una Rama para tu Feature

```bash
# SIEMPRE trabaja en una rama, NUNCA directamente en main
git checkout -b feature/nombre-descriptivo

# Ejemplos de buenos nombres de rama:
# feature/endpoint-delete-presupuesto
# fix/validacion-fechas
# docs/actualizar-api-docs
```

#### Paso 7: Hacer tus Cambios

```bash
# 1. Realiza tus cambios en el código
# 2. Prueba localmente
uvicorn app.main:app --reload

# 3. Agrega los archivos modificados
git add .

# 4. Haz commit con mensaje descriptivo
git commit -m "Add: Endpoint para eliminar presupuestos"

# 5. Sube a TU fork (origin)
git push origin feature/nombre-descriptivo
```

#### Paso 8: Crear Pull Request

1. **Ve a TU fork en GitHub:**
   ```
   https://github.com/tu-usuario/mcn_aprobaciones_backend
   ```

2. **Verás un banner amarillo** que dice:
   ```
   "feature/nombre-descriptivo had recent pushes"
   [Compare & pull request]
   ```
   Haz clic en **Compare & pull request**

3. **Configura el Pull Request:**
   - **Base repository**: `mmoyac/mcn_aprobaciones_backend`
   - **Base branch**: `main`
   - **Head repository**: `tu-usuario/mcn_aprobaciones_backend`
   - **Compare branch**: `feature/nombre-descriptivo`

4. **Llena la plantilla del PR:**
   - Título claro y descriptivo
   - Descripción completa (usa la plantilla que aparece)
   - Marca los checkboxes correspondientes

5. **Haz clic en "Create pull request"**

#### Paso 9: Esperar Revisión

- El administrador recibirá una notificación
- Revisa los comentarios si los hay
- Realiza cambios si se solicitan

#### Paso 10: Mantener tu Fork Actualizado

Antes de crear un nuevo feature, actualiza tu fork:

```bash
# Cambiar a main
git checkout main

# Traer cambios del repositorio original
git fetch upstream

# Fusionar los cambios
git merge upstream/main

# Actualizar tu fork en GitHub
git push origin main

# Ahora puedes crear una nueva rama actualizada
git checkout -b feature/nuevo-feature
```

### Opción B: Ramas en el Mismo Repositorio (Colaboradores Internos)

1. **Agregas al colaborador como colaborador:**
   - Settings → Collaborators → Add people
   - Les das permisos de **Write** (no Admin)

2. **El colaborador clona el repo:**
   ```bash
   git clone https://github.com/mmoyac/mcn_aprobaciones_backend.git
   cd mcn_aprobaciones_backend
   ```

3. **Actualiza main y crea rama:**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/nueva-funcionalidad
   ```

4. **Hace cambios y push:**
   ```bash
   git add .
   git commit -m "Add: Nueva funcionalidad"
   git push origin feature/nueva-funcionalidad
   ```

5. **Crea Pull Request en GitHub:**
   - Va al repositorio
   - Hace clic en **Pull requests** → **New pull request**
   - Selecciona: base: `main` <- compare: `feature/nueva-funcionalidad`
   - Hace clic en **Create pull request**

---

## 🔔 Cómo Te Enteras de un Pull Request

### Notificaciones Automáticas

Cuando alguien crea un PR, recibirás notificaciones de **3 formas**:

#### 1️⃣ **Email** (Automático)
- GitHub envía un email a tu dirección registrada
- Asunto: `[mmoyac/mcn_aprobaciones_backend] Título del PR (#número)`
- Contiene descripción del PR y enlace directo

#### 2️⃣ **Notificaciones de GitHub** (Campana 🔔)
- Ve a https://github.com/notifications
- Aparecerá con icono de PR
- Click para ir directamente al PR

#### 3️⃣ **Badge en el Repositorio**
- Ve a https://github.com/mmoyac/mcn_aprobaciones_backend
- Verás un número en la pestaña **Pull requests**
- Ejemplo: `Pull requests (2)` indica 2 PRs pendientes

### Configurar Notificaciones por Email

Para asegurarte de recibir emails:

1. Ve a **Settings** → **Notifications** en tu perfil de GitHub
2. En "Participating, @mentions and custom":
   - ✅ Email
   - ✅ Web and Mobile
3. En "Watching":
   - Puedes activar/desactivar según prefieras

### Ver Todos los PRs Pendientes

**URL Directa:**
```
https://github.com/mmoyac/mcn_aprobaciones_backend/pulls
```

**Filtros útiles:**
- `is:open` - Solo PRs abiertos
- `is:open is:pr author:username` - PRs de un colaborador específico
- `is:open review:required` - PRs que necesitan revisión

### Aplicación Móvil de GitHub

Puedes instalar la app móvil de GitHub para recibir notificaciones push:
- **Android**: https://play.google.com/store/apps/details?id=com.github.android
- **iOS**: https://apps.apple.com/app/github/id1477376905

---

## ✅ Proceso de Revisión (Para Ti)

### Cuando te llegue un Pull Request:

1. **Recibes notificación por email y en GitHub** (ver sección anterior)

2. **Revisas el PR:**
   - Ve a **Pull requests** en el repositorio
   - Haz clic en el PR para ver los cambios

3. **Revisa el código:**
   - Pestaña **Files changed**: Ve todos los cambios
   - Puedes agregar comentarios en líneas específicas
   - Puedes solicitar cambios

4. **Opciones:**

   **✅ Aprobar y fusionar:**
   ```
   - Haz clic en "Review changes"
   - Selecciona "Approve"
   - Haz clic en "Submit review"
   - Luego haz clic en "Merge pull request"
   - Confirma el merge
   ```

   **💬 Solicitar cambios:**
   ```
   - Haz clic en "Review changes"
   - Selecciona "Request changes"
   - Describe qué debe cambiar
   - Haz clic en "Submit review"
   ```

   **❌ Rechazar:**
   ```
   - Agrega un comentario explicando por qué
   - Haz clic en "Close pull request"
   ```

5. **Después de fusionar:**
   - La rama del PR puede eliminarse automáticamente (configurable)
   - El colaborador debe actualizar su rama local:
     ```bash
     git checkout main
     git pull origin main
     ```

---

## 📋 Plantilla de Pull Request (Opcional)

Crea el archivo `.github/PULL_REQUEST_TEMPLATE.md`:

```markdown
## 📝 Descripción

Describe brevemente los cambios realizados.

## 🎯 Tipo de cambio

- [ ] Nueva funcionalidad (feature)
- [ ] Corrección de bug (fix)
- [ ] Mejora de rendimiento (performance)
- [ ] Refactorización (refactor)
- [ ] Documentación (docs)
- [ ] Tests

## ✅ Checklist

- [ ] Mi código sigue las convenciones del proyecto
- [ ] He actualizado la documentación si es necesario
- [ ] He agregado tests que prueban mi fix/feature
- [ ] Todos los tests nuevos y existentes pasan
- [ ] He verificado que no hay conflictos con main

## 🧪 ¿Cómo se ha probado?

Describe cómo verificaste que tus cambios funcionan.

## 📸 Screenshots (si aplica)

Si es un cambio visual, agrega capturas de pantalla.

## 🔗 Issues relacionados

Closes #issue_number (si aplica)
```

---

## 🚫 Bloquear Push Directo a Main

Si configuraste correctamente la protección de rama, los colaboradores **NO podrán** hacer:

```bash
git checkout main
git push origin main  # ❌ BLOQUEADO
```

Verán un error como:
```
remote: error: GH006: Protected branch update failed
remote: error: Required status checks must pass before merging
```

---

## 🔄 Comandos de Revisión Local (Para Ti)

Si quieres probar el código del PR localmente antes de aprobar:

```bash
# Obtener el PR #1 localmente
git fetch origin pull/1/head:pr-1
git checkout pr-1

# Probar el código
uvicorn app.main:app --reload

# Si todo está bien, vuelve a main y fusiona en GitHub
git checkout main
```

---

## 📊 Configuración Recomendada

### Nivel Básico (Recomendado para empezar):
- ✅ Require pull request before merging
- ✅ Require 1 approval
- ✅ Require conversation resolution

### Nivel Intermedio:
- ✅ Todo lo anterior
- ✅ Require branches to be up to date
- ✅ Dismiss stale approvals when new commits pushed

### Nivel Avanzado (Con CI/CD):
- ✅ Todo lo anterior
- ✅ Require status checks to pass (tests, linting)
- ✅ Require linear history
- ✅ Include administrators

---

## 📝 Notas Importantes

1. **Los colaboradores siempre deben:**
   - Trabajar en ramas separadas
   - Nunca commitear directamente en `main`
   - Mantener sus ramas actualizadas con `main`
   - Escribir mensajes de commit claros

2. **Tú como administrador puedes:**
   - Aprobar o rechazar PRs
   - Solicitar cambios antes de aprobar
   - Fusionar PRs manualmente
   - Hacer push directo a `main` (si no incluiste administrators en las restricciones)

3. **Buenas prácticas:**
   - Revisar los PRs lo antes posible
   - Dar feedback constructivo
   - Usar las reviews de GitHub para comentar código específico
   - Mantener conversaciones en el PR (no por otros medios)

---

## 🆘 Ayuda Rápida

**Si un colaborador intenta push directo a main:**
```bash
# Les aparecerá error - deben hacer PR
```

**Si necesitas darle permisos temporales a alguien:**
```
Settings → Collaborators → Cambiar role a "Admin" (temporalmente)
```

**Si quieres ver todos los PRs:**
```
https://github.com/mmoyac/mcn_aprobaciones_backend/pulls
```

---

## 📧 Resumen de Notificaciones

| Método | Automático | Configuración Necesaria |
|--------|-----------|-------------------------|
| Email | ✅ Sí | Verificar en Settings → Notifications |
| Campana GitHub | ✅ Sí | Ya activado por defecto |
| Badge en Repo | ✅ Sí | Ninguna |
| App Móvil | ⚠️ Opcional | Instalar app |

### Email de Ejemplo que Recibirás:

```
De: notifications@github.com
Asunto: [mmoyac/mcn_aprobaciones_backend] Add: Endpoint para eliminar presupuestos (#1)

juanperez wants to merge 2 commits into main from feature/delete-presupuesto

Changes:
- Added new DELETE endpoint
- Updated documentation

View Pull Request: https://github.com/mmoyac/mcn_aprobaciones_backend/pull/1
```

---

¡Con esta configuración, tendrás control total sobre qué código entra a `main`! 🎉
