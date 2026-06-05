# SPEC-001 — Detección completa de incompatibilidad de BD del tenant

| | |
| :--- | :--- |
| **Estado** | 🟢 Aprobada — implementada (pendiente validación en prod, CA-6) |
| **Fecha** | 2026-06-05 |
| **Autor** | mmoyac |
| **Componentes** | Backend `/api/v1/tenant/db-check` · Frontend `DbHealthAlert.tsx` |
| **Relacionado** | [docs/AGREGAR_TENANT.md](../AGREGAR_TENANT.md) (paso 4 y gotcha #5) |

---

## 1. Contexto y problema

Cada tenant apunta a su propia base de datos MySQL (el ERP del cliente). La app espera un **esquema mínimo** en esas BD. Cuando un cliente arma su BD y le faltan columnas, la app falla.

El tablero ya tiene un panel de aviso (**"Incompatibilidad detectada en la base de datos"**, componente [`DbHealthAlert.tsx`](../../mcn_aprobaciones_frontend/components/dashboard/DbHealthAlert.tsx)) que consume el endpoint [`/tenant/db-check`](../../app/api/v1/endpoints/tenant.py). El problema es que **ese chequeo no es fiable**: valida contra una lista de columnas escrita a mano ([`REQUIRED_SCHEMA`](../../app/api/v1/endpoints/tenant.py)) que está **incompleta y desincronizada** del modelo ORM real.

### Caso real que disparó esta spec (tenant `mcn`)

- La BD `lexascl_mcn` no tenía las columnas `ocp_A4_Ap`, `ocp_A4_Dt`, `ocp_A4_Hr`, `ocp_A4_Usu` en `adq004`.
- El **dashboard contaba 14 órdenes pendientes** (el indicador hace `COUNT(ocp_nro)`, no toca esas columnas).
- Pero el **listado de órdenes salía vacío**: la query del listado hace `SELECT` de todas las columnas mapeadas por el modelo `OrdenCompra` y reventaba con `Unknown column 'adq004.ocp_A4_Ap'`.
- El **tablero marcaba `adq004` como ✅ OK**, porque `REQUIRED_SCHEMA["adq004"]` solo lista hasta el nivel A2 — no incluye A3 ni A4. **El aviso no alertó del problema que estaba rompiendo la app.**

### Causa raíz

El ORM hace `SELECT` de **todas** las columnas mapeadas de cada modelo; cualquiera ausente rompe la query. Pero el chequeo del tablero compara contra un **subconjunto curado a mano**. Las dos fuentes divergen y el aviso da falsos OK. (Esto ya estaba anotado como **gotcha #5** en el runbook de alta de tenants.)

Además, hay tablas que la app consulta con **SQL crudo** (sin modelo ORM) y que hoy **no se validan en absoluto**:
- `adq005` + `COT012` → ítems de orden de compra ([`OrdenCompraService.obtener_items`](../../app/services/orden_compra_service.py)).
- `cot005` / `cot005l` → detalle de presupuestos.

---

## 2. Objetivos y no-objetivos

### Objetivos
1. Que el panel del tablero **detecte y liste toda columna faltante que rompería la app**, sin depender de mantener listas a mano.
2. Que el chequeo quede **equivalente al script de diagnóstico autoritativo** del paso 4 del runbook.
3. **Cero mantenimiento futuro** para las tablas con modelo ORM: si se agrega una columna al modelo, el chequeo la exige automáticamente.

### No-objetivos
- No se valida **tipo, longitud ni nulabilidad** de columnas, solo **existencia** (igual que hoy).
- No se corrige automáticamente la BD del cliente (el `ALTER TABLE` lo aplica el cliente; esta spec solo mejora la **detección**).
- No se modifica el flujo de datos de negocio ni los endpoints de órdenes/presupuestos.
- No se rediseña la UI del panel (se reutiliza tal cual; el contrato de API se mantiene compatible).

---

## 3. Alcance

| Dentro | Fuera |
| :--- | :--- |
| Reescribir la lógica de `/tenant/db-check` para derivar columnas del ORM | Cambiar `DbHealthAlert.tsx` (salvo que cambie el contrato) |
| Añadir validación de tablas consultadas por SQL crudo | Validar tipos/índices/constraints |
| Mantener el contrato `DbCheckResponse` compatible | Migraciones Alembic (son tablas MySQL del cliente, no las gestionamos) |

---

## 4. Requisitos funcionales

- **RF-1.** El chequeo debe validar, por cada **modelo de negocio** (tabla en la BD MySQL del tenant), **todas** las columnas mapeadas por su modelo ORM.
- **RF-2.** El chequeo debe validar, por cada **tabla de SQL crudo** registrada, la lista de columnas que la app referencia en sus queries.
- **RF-3.** Si una tabla no existe, debe reportarse como `existe=false`, `ok=false` y listar todas sus columnas requeridas como faltantes (comportamiento actual).
- **RF-4.** La comparación de nombres de columnas debe ser **case-insensitive** (comportamiento actual).
- **RF-5.** `tiene_errores` debe ser `true` si cualquier tabla tiene `ok=false`.
- **RF-6.** El endpoint **no debe romperse** si un `DESCRIBE`/`SHOW TABLES` falla para una tabla puntual; debe degradar a reportar esa tabla como problemática, no tirar 500.
- **RF-7.** Los modelos que viven en **PostgreSQL** (`Tenant`, `TenantTema`, `TenantConexion`, `DocumentoPDF`) **no** deben validarse contra la BD MySQL del tenant.

---

## 5. Diseño técnico

### 5.1. Distinguir modelos de negocio (MySQL del tenant)

Como todos los modelos comparten `Base`, se define una **lista explícita** de modelos de negocio a validar (legible y a prueba de errores frente a iterar todo `Base.registry`):

```python
# app/api/v1/endpoints/tenant.py
from app.models.orden_compra import OrdenCompra
from app.models.presupuesto import Presupuesto
from app.models.cliente import Cliente
from app.models.proveedor import Proveedor
from app.models.local import Local
from app.models.usuario import Usuario

# Modelos cuyas tablas viven en la BD MySQL del tenant (ERP del cliente)
BUSINESS_MODELS = [OrdenCompra, Presupuesto, Cliente, Proveedor, Local, Usuario]
```

Para cada modelo se derivan las columnas requeridas desde el mapper:

```python
def _required_cols(model) -> tuple[str, list[str]]:
    mapper = sa_inspect(model)
    return mapper.local_table.name, [col.name for col in mapper.columns]
```

> **Nota:** esto exige importar explícitamente `Local` (hoy solo se importa desde el service), para garantizar que esté registrado en el `Base.registry` cuando corre el endpoint.

### 5.2. Tablas de SQL crudo

Las tablas sin modelo ORM se mantienen en una constante chica y explícita, poblada con las columnas que la app referencia en sus queries:

```python
RAW_SQL_SCHEMA = {
    # ítems de orden de compra — OrdenCompraService.obtener_items
    "adq005": ["Loc_cod", "ocp_nro", "ocp_lin", "ocp_mat", "Ocp_Odt",
               "Ocp_De1", "Ocp_De2", "Ocp_De3", "Ocp_est", "Ocp_can", "Ocp_pre"],
    "COT012": ["mat_cod", "mat_des"],
    # detalle de presupuestos
    "cot005":  ["loc_cod", "pre_nro", "pre_lin", "pre_des", "pre_de1", "pre_de2",
                "pre_de3", "pre_de4", "pre_cpr", "pre_pre", "pre_dct"],
    "cot005l": ["loc_cod", "pre_nro", "pre_lin", "pre_dtlin", "Pre_DtTip",
                "Pre_DtCant", "Pre_DtPre", "Pre_DtDescrip"],
}
```

> Estas listas se derivan de las queries en `OrdenCompraService` y `PresupuestoService` y del script del paso 4 del runbook. Quedan documentadas con un comentario que apunta al método que las usa, para que se actualicen si cambia el SQL.

### 5.3. Algoritmo del endpoint

1. `SHOW TABLES` → set de tablas existentes (lower).
2. Construir `schema_requerido = { tabla: columnas }` combinando:
   - `BUSINESS_MODELS` (vía `_required_cols`)
   - `RAW_SQL_SCHEMA`
3. Para cada `(tabla, columnas)`:
   - Si no existe → `existe=false`, `ok=false`, faltantes = todas.
   - Si existe → `DESCRIBE` → faltantes = columnas no presentes (case-insensitive). `ok = not faltantes`.
   - Envolver el `DESCRIBE` por tabla en try/except (RF-6).
4. `tiene_errores = any(not c.ok)`.
5. Devolver `DbCheckResponse` (sin cambios de forma).

### 5.4. Contrato de API

**Sin cambios** en `DbCheckResponse` / `TableCheck`. El frontend `DbHealthAlert.tsx` sigue funcionando igual; solo cambiará el **contenido** (más tablas y columnas reportadas). `columnas_extra` se mantiene como `[]` (no se usa hoy).

### 5.5. Frontend

Sin cambios de código. Como ahora pueden aparecer más tablas en `checks`, conviene verificar visualmente que la lista expandible se ve bien con ~8-10 tablas (hoy muestra 5).

---

## 6. Criterios de aceptación

- **CA-1.** Dado el tenant `mcn` con `adq004` sin las columnas `ocp_A4_*`, el endpoint reporta `adq004` con `ok=false` y `columnas_faltantes` incluye `ocp_A4_Ap, ocp_A4_Dt, ocp_A4_Hr, ocp_A4_Usu`. ✅ (hoy falla: lo marca OK)
- **CA-2.** Tras aplicar el `ALTER TABLE` en `lexascl_mcn`, el endpoint reporta `adq004` con `ok=true`.
- **CA-3.** Para un tenant 100% compatible (ej. `mga`), `tiene_errores=false` y todas las tablas `ok=true`.
- **CA-4.** Si falta una columna que la app usa solo por SQL crudo (ej. `adq005.Ocp_can`), el endpoint la reporta como faltante.
- **CA-5.** Las tablas de PostgreSQL (`tenants`, `tenant_temas`, etc.) **no** aparecen en `checks`.
- **CA-6.** El resultado del endpoint coincide con el del script de diagnóstico del paso 4 del runbook para los tenants `mga`, `mgacom`, `mgamaq`, `mcn`.

## 7. Plan de pruebas

- **Test unitario** del armado de `schema_requerido`: que `BUSINESS_MODELS` produce las tablas esperadas y que `adq004` incluye las 25 columnas del modelo (incluidas A3/A4).
- **Test de integración** con una BD MySQL de prueba (o mock de `DESCRIBE`) que simule columnas faltantes y verifique `columnas_faltantes`.
- **Validación manual en prod** contra los 4 tenants (CA-6), comparando con el script del paso 4.

## 8. Riesgos y consideraciones

- **R-1 — Más ruido en el panel.** Al exigir todas las columnas del ORM, tenants que "funcionaban a medias" pueden empezar a mostrar avisos (ej. `ctbm01` pasa de exigir 3 a 15 columnas; `cot013` de 18 a todas las del modelo). _Mitigación:_ es el comportamiento correcto (esas columnas el ORM las pide igual); revisar el impacto en `mga/mgacom/mgamaq` antes de desplegar y avisar a los clientes afectados.
- **R-2 — Costo de round-trips al MySQL remoto.** Hacer `SHOW TABLES` + un `DESCRIBE` por tabla son ~11 viajes secuenciales; contra un MySQL remoto (~40 ms/viaje) eso da ~0.5 s. **Resuelto:** el endpoint hace ahora **una sola** consulta a `information_schema.COLUMNS` (1 viaje) y baja a ~0.2 s. El frontend además cachea 60 s.
- **R-3 — `RAW_SQL_SCHEMA` puede desincronizarse** si cambia el SQL crudo. _Mitigación:_ comentario que apunta al método fuente; idealmente, a futuro, mover esas queries a modelos ORM.

## 9. Fuera de alcance / mejoras futuras

- Validar tipos/longitud/nulabilidad de columnas.
- Mapear `adq005`/`COT012`/`cot005`/`cot005l` como modelos ORM para eliminar `RAW_SQL_SCHEMA`.
- Endpoint que genere el `ALTER TABLE` sugerido por tenant (auto-documentación de compatibilidad).

## 10. Plan de implementación

1. ✅ Refactor de [`tenant.py`](../../app/api/v1/endpoints/tenant.py): `BUSINESS_MODELS` + `build_required_schema()` + `RAW_SQL_SCHEMA`, reemplazando `REQUIRED_SCHEMA`.
2. ✅ Importar `Local` (y demás modelos de negocio) explícitamente.
3. ✅ Tests en [`tests/api/test_db_check_schema.py`](../../tests/api/test_db_check_schema.py) — 6 tests, todos en verde (lógica pura, sin BD).
4. ⏳ Validación en prod contra los 4 tenants (CA-6).
5. ⏳ Actualizar runbook (gotcha #5 deja de aplicar) y documentar.
