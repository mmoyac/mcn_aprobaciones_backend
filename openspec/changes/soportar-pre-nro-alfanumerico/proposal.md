# Proposal

## Why

En el tenant **mcn** el tablero muestra 547 presupuestos pendientes, pero el listado sale vacío y "Aprobados Hoy" falla: el endpoint responde **500**. La causa es que en la BD del ERP de mcn (`lexascl_mcn`) el número de presupuesto `pre_nro` es `char(12)` con formato `NNNNN-AAAA-V` (ej. `06798-2026-0`), mientras que la app asume que es un entero (`BIGINT`), que es lo que usan gontec, mga, mgamaq y mgacom. No se puede resolver en la BD: el formato es propio del ERP del cliente y no se puede convertir a número sin perder información.

Verificado en producción el 2026-09-30 (solo lectura):

| Tenant | `cot013/cot005/cot005l/cot017/cot018.pre_nro` | `adq004/adq005.ocp_nro` |
| :--- | :--- | :--- |
| gontec, mga, mgamaq, mgacom | `bigint(20)` | `bigint(20)` |
| **mcn** | **`char(12)`** | `bigint(20)` |

`lexascl_reppdf.pdf001.PdfNumero` es `bigint(20)` para todos.

## What Changes

- La app pasa a aceptar el identificador de presupuesto (`pre_nro`) como **número o texto**, según lo que entregue la BD de cada tenant, en todo el módulo de presupuestos: indicadores, pendientes, aprobados, histórico, detalle, aprobar, anular y desaprobar.
- **Se mantiene el contrato con los tenants numéricos:** si en la BD `pre_nro` es numérico, la API lo sigue devolviendo como número JSON. Solo los tenants con `pre_nro` alfanumérico reciben un string. No hay cambios visibles para gontec, mga, mgamaq ni mgacom.
- Los endpoints que reciben `pre_nro` (en la ruta `/{loc_cod}/{pre_nro}/detalle` y en el body de aprobar, anular y desaprobar) aceptan ambos formatos.
- **Corrección de seguridad de datos en PDFs (REPPDF):**
  - La verificación en lote hoy arma `PdfNumero IN (06798-2026-0, …)` sin comillas, y MySQL lo evalúa como una resta.
  - Al aprobar, el borrado del PDF compararía `'06798-2026-0'` contra un `BIGINT`, y MySQL lo convertiría a `6798`, con riesgo de borrar un PDF equivocado.
  - Los números no numéricos se tratan como "sin PDF" y **nunca** se usan en consultas contra `pdf001`.
- **Frontend:**
  - Los tipos de `pre_nro` pasan de `number` a `number | string`.
  - La página de detalle deja de hacer `Number(params.pre_nro)`, que produce `NaN` con valores de mcn.
  - Los enlaces y los PDFs funcionan con ambos formatos.

**Fuera de alcance:**
- **Guardar y ver PDFs de presupuestos alfanuméricos:** requiere cambiar `pdf001`, que es compartida por todos los tenants. Se hará en otra spec.
- **Enseñarle a `/tenant/db-check` a detectar divergencias de tipo:** queda como mejora de seguimiento.
- **Órdenes de compra:** mcn usa `bigint`, así que no cambian.

## Capabilities

### New Capabilities
- `presupuestos/identificador-presupuesto`: cómo la app identifica, expone y recibe el número de presupuesto (`pre_nro`) de forma agnóstica al tipo de columna de cada tenant (numérico o alfanumérico), incluido el tratamiento seguro frente a REPPDF.

### Modified Capabilities
<!-- No hay specs existentes en openspec/specs/ (proyecto recién inicializado en OpenSpec). -->

## Impact

- **Backend:**
  - `app/models/presupuesto.py`: tipo de la columna `pre_nro`.
  - `app/schemas/presupuesto.py` y `app/schemas/presupuesto_detalle.py`: `pre_nro: int` pasa a aceptar número o texto.
  - `app/api/v1/endpoints/presupuestos.py`: parámetro de ruta y bodies.
  - `app/services/presupuesto_service.py`: firmas; `_verificar_pdfs_batch` y `_eliminar_pdf_reppdf`.
- **Frontend (repo `mcn_aprobaciones_frontend`, rama propia):**
  - `lib/types/index.ts`, `lib/api/presupuestos.ts`.
  - Páginas `dashboard/presupuestos`, `dashboard/presupuestos/[loc_cod]/[pre_nro]` y `dashboard/historico`.
- **API:** no rompe a los tenants numéricos. El campo `pre_nro` se documenta en OpenAPI como `integer | string`. Los consumidores externos (por ejemplo el flujo n8n) siguen recibiendo enteros para los tenants actuales.
- **BD:** ningún cambio de esquema en ningún tenant ni en REPPDF.
- **Tests:**
  - Tests nuevos con BD de prueba local con ambos tipos, que cubren también las escrituras.
  - Validación manual en la app: hojas de datos por tenant, generadas con consultas de solo lectura a las 5 BD reales, que el usuario corrobora antes y después del deploy.
