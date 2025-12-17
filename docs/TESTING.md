# 📋 Testing Guidelines - MCN Aprobaciones Backend

## 🧪 Guía de Ejecución de Tests

### ⚠️ IMPORTANTE: Arquitectura Dual de Base de Datos

Este proyecto utiliza **dos bases de datos**:
- **PostgreSQL**: Para documentos PDF (endpoints `/documentos-pdf/*`)
- **MySQL**: Para datos legacy (presupuestos, usuarios, etc.)

### 📦 Prerequisitos OBLIGATORIOS

**TODOS los tests con persistencia requieren contenedores Docker ejecutándose:**

```bash
# 1. Iniciar contenedores (OBLIGATORIO)
docker-compose up -d

# 2. Verificar estado
docker ps
# Debe mostrar:
# - mcn_aprobaciones_backend (puerto 8000)
# - mcn_aprobaciones_postgres (puerto 5432)

# 3. Verificar conectividad
docker exec mcn_aprobaciones_postgres pg_isready -U lexasdulce
```

### 🎯 Tipos de Tests

#### Tests Unitarios (sin DB)
```bash
# Tests que no requieren base de datos
pytest tests/unit/ -v
```

#### Tests de Integración (con DB)
```bash
# REQUIEREN contenedores Docker corriendo

# Tests PostgreSQL (documentos PDF)
pytest tests/api/test_documento_pdf.py -v

# Tests MySQL (presupuestos, usuarios)  
pytest tests/api/test_presupuestos.py -v
pytest tests/api/test_usuarios.py -v

# Todos los tests API
pytest tests/api/ -v
```

#### Test Suite Completo
```bash
# Ejecutar TODOS los tests (requiere contenedores)
pytest

# Con cobertura detallada
pytest --cov=app --cov-report=html --cov-report=term-missing

# Solo tests que pasaron en último run
pytest --lf
```

### 🔧 Configuración de Test Environment

#### Variables de Entorno (conftest.py)
```python
# Configuración automática para tests:
POSTGRES_HOST = "localhost"     # Conectar desde host a container
POSTGRES_PORT = "5432"         # Puerto expuesto del container
API_KEY = "supersecreta123"     # API key para endpoints PDF
```

#### ¿Por qué localhost y no postgres?
- **En contenedor**: app usa `POSTGRES_HOST=postgres` (network interno)
- **En tests**: necesitamos `POSTGRES_HOST=localhost` (desde host)
- **conftest.py** sobrescribe automáticamente para tests

### 🚨 Errores Comunes y Soluciones

#### Error: `could not translate host name "postgres"`
```bash
# Problema: Contenedores no están corriendo
# Solución:
docker-compose up -d
```

#### Error: `Connection refused` puerto 5432
```bash
# Problema: PostgreSQL no está disponible
# Solución:
docker ps | grep postgres  # Verificar contenedor
docker logs mcn_aprobaciones_postgres  # Ver logs
```

#### Tests fallan con 500 Internal Server Error
```bash
# Problema: Contenedor backend no actualizado
# Solución:
docker-compose down
docker-compose up --build -d
```

#### Error: `API key missing or invalid`
```bash
# Problema: Variable API_KEY no configurada
# Verificar: conftest.py tiene os.environ["API_KEY"] = "supersecreta123"
```

### 📊 Flujo Recomendado de Testing

#### Desarrollo Local
```bash
# 1. Desarrollo de código
vim app/api/v1/endpoints/documento_pdf.py

# 2. Iniciar entorno (si no está corriendo)
docker-compose up -d

# 3. Test específico durante desarrollo  
pytest tests/api/test_documento_pdf.py::test_get_documento_pdf_success -v

# 4. Test completo antes de commit
pytest tests/api/test_documento_pdf.py -v

# 5. Suite completa antes de push
pytest --cov=app
```

#### CI/CD (GitHub Actions)
```yaml
# Los workflows automáticamente:
# 1. Levantan servicios PostgreSQL/MySQL
# 2. Configuran variables de entorno
# 3. Ejecutan pytest con cobertura
# 4. Publican reportes
```

### 📝 Mejores Prácticas

1. **Siempre** iniciar contenedores antes de tests con DB
2. **Nunca** commitear tests que dependan de datos específicos existentes
3. **Usar** números únicos en tests (ej: timestamp) para evitar colisiones
4. **Verificar** que tests puedan ejecutarse múltiples veces sin fallar
5. **Limpiar** datos de test si es necesario (aunque no es crítico en entorno de desarrollo)

### 🔍 Debug de Tests

#### Ver qué está en la base de datos
```bash
# PostgreSQL - documentos PDF
docker exec -it mcn_aprobaciones_postgres psql -U lexasdulce -d lexascl_gontec -c "SELECT id, tipo, numero FROM documentos_pdf LIMIT 5;"

# Logs de la aplicación
docker logs mcn_aprobaciones_backend --tail 20

# Test con output detallado
pytest tests/api/test_documento_pdf.py -v -s --tb=short
```

---

**📌 Recuerda**: Los contenedores Docker NO son opcionales para tests con base de datos. Son un prerequisito fundamental para que funcione la persistencia y conectividad correctamente.