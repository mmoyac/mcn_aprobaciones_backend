# 🔗 Información del Repositorio

## Repositorio GitHub

**URL**: https://github.com/mmoyac/mcn_aprobaciones_backend

## Configuración Git

```bash
# Clonar el repositorio
git clone https://github.com/mmoyac/mcn_aprobaciones_backend.git
cd mcn_aprobaciones_backend

# Verificar remote
git remote -v
```

## Estructura del Commit Inicial

**Commit**: `Initial commit: Backend MCN Aprobaciones con FastAPI y MySQL`

**Branch principal**: `main`

**Archivos incluidos**: 31 archivos

### Contenido del Repositorio:

- ✅ Código fuente completo (`app/`)
- ✅ Documentación (`docs/`, `README.md`, `AGENTS.md`)
- ✅ Configuración de proyecto (`.gitignore`, `requirements.txt`, `pytest.ini`)
- ✅ Esquema de base de datos (`schema/db_tables.sql`)
- ✅ Tests configurados (`tests/`)
- ✅ Variables de entorno de ejemplo (`.env.example`)

## Comandos Git Útiles

```bash
# Ver estado del repositorio
git status

# Crear una nueva rama
git checkout -b feature/nueva-funcionalidad

# Agregar cambios
git add .
git commit -m "Descripción del cambio"

# Subir cambios
git push origin main

# Actualizar desde GitHub
git pull origin main

# Ver historial
git log --oneline
```

## Archivos NO Versionados (en .gitignore)

- `.env` - Variables de entorno reales
- `.venv/` - Entorno virtual de Python
- `__pycache__/` - Archivos compilados de Python
- `*.pyc` - Bytecode de Python
- `.coverage` - Archivos de cobertura de tests
- `*.log` - Archivos de log

## Configuración Local de Git

```bash
# Ver configuración actual
git config --list

# Cambiar usuario/email si es necesario
git config user.name "Tu Nombre"
git config user.email "tu.email@ejemplo.com"
```

## Colaboración

Para colaborar en este proyecto:

1. **Fork** el repositorio
2. Crea una **rama** para tu feature: `git checkout -b feature/AmazingFeature`
3. **Commit** tus cambios: `git commit -m 'Add some AmazingFeature'`
4. **Push** a la rama: `git push origin feature/AmazingFeature`
5. Abre un **Pull Request**

## CI/CD (Futuro)

Próximos pasos para automatización:

- [ ] GitHub Actions para tests automáticos
- [ ] Linting automático con Black y Ruff
- [ ] Deploy automático a servidor
- [ ] Badges de estado en README

## Protección de Ramas

Se recomienda configurar protección para la rama `main`:

- Requerir pull request reviews
- Requerir que los tests pasen
- No permitir force push

## Enlaces Útiles

- **Repositorio**: https://github.com/mmoyac/mcn_aprobaciones_backend
- **Issues**: https://github.com/mmoyac/mcn_aprobaciones_backend/issues
- **Pull Requests**: https://github.com/mmoyac/mcn_aprobaciones_backend/pulls

---

**Última actualización**: Diciembre 5, 2025
