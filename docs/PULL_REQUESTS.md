# 🔒 Configuración de Protección de Ramas y Pull Requests

Esta guía explica cómo configurar el repositorio para que los colaboradores trabajen mediante Pull Requests que requieren aprobación.

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

1. **El colaborador hace Fork:**
   - Va a https://github.com/mmoyac/mcn_aprobaciones_backend
   - Hace clic en **Fork** (arriba a la derecha)
   - Clona su fork:
     ```bash
     git clone https://github.com/su-usuario/mcn_aprobaciones_backend.git
     cd mcn_aprobaciones_backend
     ```

2. **Configura el repositorio original como upstream:**
   ```bash
   git remote add upstream https://github.com/mmoyac/mcn_aprobaciones_backend.git
   ```

3. **Crea una rama para su feature:**
   ```bash
   git checkout -b feature/nueva-funcionalidad
   ```

4. **Hace sus cambios y commits:**
   ```bash
   git add .
   git commit -m "Add: Nueva funcionalidad"
   git push origin feature/nueva-funcionalidad
   ```

5. **Crea Pull Request:**
   - Va a su fork en GitHub
   - Hace clic en **Compare & pull request**
   - Llena la descripción del PR
   - Selecciona base: `mmoyac/main` <- compare: `su-usuario/feature/nueva-funcionalidad`
   - Hace clic en **Create pull request**

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
