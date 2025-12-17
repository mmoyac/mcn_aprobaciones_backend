# 📚 Documentación API - Presupuestos

## Descripción General

API REST para gestionar y consultar presupuestos del sistema MCN Aprobaciones. Proporciona endpoints para obtener indicadores y listar presupuestos según su estado de aprobación.

## Base URL

```
http://localhost:8000/api/v1
```

## Autenticación

*Por implementar en futuras versiones*

---

## 📊 Endpoints de Indicadores

### GET /presupuestos/indicadores

Obtiene los indicadores principales de presupuestos: totales de pendientes y aprobados.

#### Respuesta Exitosa (200)

```json
{
  "pendientes": 15,
  "aprobados": 234
}
```

#### Campos de Respuesta

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `pendientes` | integer | Total de presupuestos liberados pero pendientes de aprobación final (Pre_vbLib=1 AND pre_vbgg=0) |
| `aprobados` | integer | Total de presupuestos aprobados por gerencia (pre_vbgg=1) |

#### Ejemplo de Uso

```bash
curl -X GET "http://localhost:8000/api/v1/presupuestos/indicadores"
```

```python
import requests

response = requests.get("http://localhost:8000/api/v1/presupuestos/indicadores")
indicadores = response.json()
print(f"Pendientes: {indicadores['pendientes']}")
print(f"Aprobados: {indicadores['aprobados']}")
```

---

## 📋 Endpoints de Listados

### GET /presupuestos/pendientes

Lista los presupuestos pendientes de aprobación final con validación automática de PDF asociado.

#### Parámetros de Query

| Parámetro | Tipo | Requerido | Default | Descripción |
|-----------|------|-----------|---------|-------------|
| `skip` | integer | No | 0 | Número de registros a omitir (paginación) |
| `limit` | integer | No | 100 | Cantidad máxima de registros (máx: 1000) |

#### Criterio de Filtrado

- `Pre_vbLib = 1` - Presupuesto liberado
- `pre_vbgg = 0` - Pendiente de aprobación de gerencia
- **Enriquecimiento PDF**: Cada registro incluye validación automática de PDF asociado

#### Respuesta Exitosa (200)

```json
[
  {
    "Loc_cod": 1,
    "pre_nro": 1234567,
    "pre_est": "A",
    "pre_fec": "2025-12-01",
    "pre_rut": 12345678,
    "pre_VenCod": 10,
    "Pre_Neto": 1500000,
    "Pre_vbLib": 1,
    "pre_vbgg": 0,
    "pre_gl1": "Presupuesto para proyecto X",
    "pre_fecAdj": "2025-12-05",
    "pre_VbLibUsu": "ADMIN",
    "Pre_VBLibDt": "2025-12-02",
    "pre_vbggUsu": "",
    "pre_vbggDt": null,
    "pre_trnFec": "2025-12-01",
    "pre_trnusu": "VENDEDOR1",
    "tienepdf": 1
  }
]
```

#### Ejemplo de Uso

```bash
# Obtener primeros 10 presupuestos pendientes
curl -X GET "http://localhost:8000/api/v1/presupuestos/pendientes?limit=10"

# Obtener página 2 (registros 50-100)
curl -X GET "http://localhost:8000/api/v1/presupuestos/pendientes?skip=50&limit=50"
```

```python
import requests

# Obtener presupuestos pendientes con paginación
params = {"skip": 0, "limit": 50}
response = requests.get(
    "http://localhost:8000/api/v1/presupuestos/pendientes",
    params=params
)
presupuestos = response.json()

for presup in presupuestos:
    pdf_status = "Con PDF" if presup['tienepdf'] == 1 else "Sin PDF"
    print(f"Presupuesto #{presup['pre_nro']} - Monto: ${presup['Pre_Neto']:,} - {pdf_status}")
```

---

### GET /presupuestos/aprobados

Lista los presupuestos aprobados por gerencia.

#### Parámetros de Query

| Parámetro | Tipo | Requerido | Default | Descripción |
|-----------|------|-----------|---------|-------------|
| `skip` | integer | No | 0 | Número de registros a omitir (paginación) |
| `limit` | integer | No | 100 | Cantidad máxima de registros (máx: 1000) |

#### Criterio de Filtrado

- `pre_vbgg = 1` - Aprobado por gerencia general

#### Respuesta Exitosa (200)

```json
[
  {
    "Loc_cod": 1,
    "pre_nro": 1234560,
    "pre_est": "A",
    "pre_fec": "2025-11-28",
    "pre_rut": 98765432,
    "pre_VenCod": 15,
    "Pre_Neto": 2800000,
    "Pre_vbLib": 1,
    "pre_vbgg": 1,
    "pre_gl1": "Presupuesto proyecto Y aprobado",
    "pre_fecAdj": "2025-11-30",
    "pre_VbLibUsu": "ADMIN",
    "Pre_VBLibDt": "2025-11-29",
    "pre_vbggUsu": "GERENTE1",
    "pre_vbggDt": "2025-11-30",
    "pre_trnFec": "2025-11-28",
    "pre_trnusu": "VENDEDOR2"
  }
]
```

#### Ejemplo de Uso

```bash
# Obtener primeros 20 presupuestos aprobados
curl -X GET "http://localhost:8000/api/v1/presupuestos/aprobados?limit=20"
```

```python
import requests

# Obtener presupuestos aprobados
response = requests.get(
    "http://localhost:8000/api/v1/presupuestos/aprobados",
    params={"limit": 100}
)
presupuestos = response.json()

print(f"Total aprobados obtenidos: {len(presupuestos)}")
```

---

## 📄 Modelo de Datos: PresupuestoDetalle

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `Loc_cod` | integer | Código de local |
| `pre_nro` | integer | Número de presupuesto (único) |
| `pre_est` | string | Estado del presupuesto (1 carácter) |
| `pre_fec` | date | Fecha del presupuesto (formato: YYYY-MM-DD) |
| `pre_rut` | integer | RUT del cliente |
| `pre_VenCod` | integer | Código del vendedor |
| `Pre_Neto` | integer | Monto neto del presupuesto |
| `Pre_vbLib` | integer | VB Liberación (1=aprobado, 0=no) |
| `pre_vbgg` | integer | VB Gerencia (1=aprobado, 0=no) |
| `pre_gl1` | string | Glosa/descripción línea 1 |
| `pre_fecAdj` | date | Fecha de adjudicación |
| `pre_VbLibUsu` | string | Usuario que dio VB liberación |
| `Pre_VBLibDt` | date | Fecha VB liberación |
| `pre_vbggUsu` | string | Usuario que dio VB gerencia |
| `pre_vbggDt` | date | Fecha VB gerencia |
| `pre_trnFec` | date | Fecha de transacción |
| `pre_trnusu` | string | Usuario de transacción |
| `tienepdf` | integer | Indica si tiene PDF asociado (1=sí, 0=no) **[Solo en /pendientes]** |

---

## 🔍 Códigos de Estado HTTP

| Código | Descripción |
|--------|-------------|
| 200 | Respuesta exitosa |
| 400 | Parámetros inválidos (ej: limit > 1000) |
| 500 | Error interno del servidor |

---

## 💡 Lógica de Negocio

### Estados de Aprobación

El sistema maneja tres estados principales para un presupuesto:

1. **Creado**: Presupuesto inicial sin aprobaciones
   - `Pre_vbLib = 0`
   - `pre_vbgg = 0`

2. **Pendiente**: Liberado pero esperando aprobación de gerencia
   - `Pre_vbLib = 1` ✅
   - `pre_vbgg = 0` ⏳
   - **Validación PDF automática**: Campo `tienepdf` indica presencia de documento

3. **Aprobado**: Aprobación final de gerencia
   - `pre_vbgg = 1` ✅

### Flujo de Aprobación

```
Creado → Liberación → Pendiente → Aprobación Gerencia → Aprobado
        (Pre_vbLib=1)            (pre_vbgg=1)
```

---

## 🚀 Documentación Interactiva

La API incluye documentación interactiva automática:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Estas interfaces permiten probar los endpoints directamente desde el navegador.

---

## � Integración PDF

### Validación Automática de PDFs

El endpoint `/presupuestos/pendientes` incluye validación automática de PDFs asociados:

- **Campo `tienepdf`**: Valor calculado dinámicamente (1=existe PDF, 0=no existe)
- **Método de validación**: HTTP interno al endpoint `/api/v1/documentos-pdf/get`
- **Timeout**: 5 segundos para evitar bloqueos
- **Manejo de errores**: En caso de fallo, `tienepdf=0` (asume sin PDF)

#### Implementación Técnica

```python
# Ejemplo de validación interna
async def _verificar_pdf_existe(pre_nro: int) -> int:
    try:
        response = await httpx.get(
            f"http://127.0.0.1:8000/api/v1/documentos-pdf/get",
            params={"pre_nro": pre_nro},
            headers={"x-api-key": "supersecreta123"},
            timeout=5.0
        )
        return 1 if response.status_code == 200 else 0
    except:
        return 0  # Asume sin PDF en caso de error
```

---

## 📝 Notas Adicionales

- Los listados están ordenados por fecha descendente
- El límite máximo por consulta es de 1000 registros
- Se recomienda usar paginación para grandes volúmenes de datos
- Todos los endpoints retornan JSON
- Los campos de fecha siguen el formato ISO 8601 (YYYY-MM-DD)
- **TDD**: Funcionalidad desarrollada con Test-Driven Development (8 tests)
