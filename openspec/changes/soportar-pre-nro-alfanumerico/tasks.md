# Tasks

## 1. Datos de validación (antes de tocar código)

- [x] 1.1 Crear `scripts/datos_validacion.py`. Por cada tenant (gontec, mga, mgamaq, mgacom, mcn) ejecuta solo `SELECT` contra su BD y genera una hoja en Markdown con: cantidad de pendientes y aprobados hoy, los 5 primeros pendientes (número, fecha, cliente, neto) en el orden del listado, y los ítems y aprobaciones de 1 presupuesto. Verificar que el script no contiene sentencias de escritura (test que busca `INSERT|UPDATE|DELETE|ALTER` en las consultas y falla si las encuentra).
- [ ] 1.2 Generar las hojas y entregarlas al usuario. Verificar que el usuario confirma que coinciden con la app **actual** en los 4 tenants numéricos, y que en mcn el tablero coincide pero el listado sale vacío (reproduce el bug).

## 2. Infraestructura de pruebas de integración (MySQL local)

- [x] 2.1 Crear `docker-compose.test.yml` con MySQL 5.7 y un script de inicialización que genere, desde `schema/db_tables.sql`, dos esquemas de negocio: `t_numerico` con `pre_nro BIGINT` y `t_alfanumerico` con `pre_nro CHAR(12)` en `cot013`, `cot005`, `cot005l`, `cot017` y `cot018`, más un esquema `t_reppdf` con `pdf001`. Verificar con `docker compose -f docker-compose.test.yml up -d` y un `SELECT` a `information_schema` que ambos tipos quedaron como se espera.
- [x] 2.2 Cargar datos semilla con casos límite:
  - presupuestos pendientes y aprobados hoy en ambos esquemas;
  - en `t_alfanumerico`, `06798-2026-0` y `06798-2026-1`, y un presupuesto con ceros a la izquierda;
  - en `t_numerico`, el `6798`;
  - ítems `cot005`/`cot005l`, aprobaciones `cot012`, clientes `clientea`, sucursales `loc001` y un usuario `ctbm01`;
  - en `pdf001`, un PDF numérico `6798` para tenant alfanumérico y numérico.

  Verificar contando filas por tabla.
- [x] 2.3 Crear fixtures pytest en `tests/integration/conftest.py`:
  - `TestClient` de la app con `get_tenant_db` sobrescrito por esquema;
  - sesión REPPDF apuntando a `t_reppdf`;
  - JWT de prueba emitido con una `SECRET_KEY` de test;
  - marca `@pytest.mark.integration` que se salta si el MySQL de prueba no está arriba.

  Verificar con un test humo que `GET /presupuestos/indicadores` responde 200 en ambos esquemas.
- [x] 2.4 Escribir los tests de integración de la spec **antes** del cambio: pendientes, aprobados, histórico, detalle, aprobar, anular, desaprobar y PDFs, para ambos esquemas. Verificar que en `t_numerico` pasan y en `t_alfanumerico` fallan con la versión actual (esa falla reproduce el bug).

## 3. Backend: identificador agnóstico al tipo

- [x] 3.1 Cambiar `pre_nro` a `Union[int, str]` en todos los schemas de `app/schemas/presupuesto.py` y `app/schemas/presupuesto_detalle.py`, y actualizar los ejemplos OpenAPI. Verificar con tests unitarios que `12345` se serializa como número, `"06798-2026-0"` y `"00123"` como string, y que `/openapi.json` expone `integer | string`.
- [x] 3.2 Cambiar la columna `Presupuesto.pre_nro` del modelo a `String(20)`, sin tocar la BD (D3). Verificar con un test de integración que en `t_numerico` el valor leído sigue siendo `int` y en `t_alfanumerico` es `str`. Si falla, aplicar el plan B (`TypeDecorator`) y dejarlo anotado en design.md.
- [x] 3.3 Cambiar el parámetro de ruta `pre_nro` del detalle a `str` con validación de longitud máxima 20 y patrón `^[0-9A-Za-z\-]+$`, y ajustar las firmas `pre_nro: int` de `presupuesto_service.py` (detalle, aprobar, anular, desaprobar). Verificar que los tests de detalle pasan en ambos esquemas y que una ruta con caracteres inválidos devuelve 422.
- [x] 3.4 Verificar que los tests de integración de pendientes, aprobados, histórico, aprobar, anular y desaprobar (tarea 2.4) pasan en ambos esquemas. Incluye:
  - aprobar `06798-2026-0` no toca `06798-2026-1`;
  - un `pre_nro` inexistente da 404 sin cambios en la BD;
  - un `pre_nro` numérico enviado como string `"12345"` en un tenant numérico funciona.

## 4. Backend: seguridad de PDFs en REPPDF

- [x] 4.1 Implementar `_es_numero_reppdf` (D4) con tests unitarios: `int` → sí; `"6798"` → sí; `"06798-2026-0"`, `"-1"`, `""`, `"9"*20` → no.
- [x] 4.2 Reescribir `_verificar_pdfs_batch`: parámetros enlazados (`bindparam(expanding=True)`) solo para los números válidos, `tienepdf = 0` para el resto sin consultar, y claves de `pdf_map` normalizadas. Verificar con tests de integración que:
  - en `t_numerico` el `tienepdf` es el mismo que antes;
  - en `t_alfanumerico` todo sale `0`;
  - un listener de SQLAlchemy confirma que no se envía a REPPDF ninguna consulta con identificadores alfanuméricos.
- [x] 4.3 Hacer que `_eliminar_pdf_reppdf` omita (con log) los números no numéricos. Verificar con un test de integración que aprobar `06798-2026-0` deja intacto el PDF `6798` de `pdf001`, y que aprobar en `t_numerico` sigue borrando el PDF correspondiente.

## 5. Frontend (repo `mcn_aprobaciones_frontend`, rama `feat/pre-nro-alfanumerico`)

- [x] 5.1 Cambiar `pre_nro` a `number | string` en `lib/types/index.ts` y en las firmas de `lib/api/presupuestos.ts` (`getDetalle`, `getPDF`). Codificar el número en las URLs con `encodeURIComponent`. Verificar con `npx tsc --noEmit` sin errores.
- [x] 5.2 Página `dashboard/presupuestos/[loc_cod]/[pre_nro]`: reemplazar `Number(params.pre_nro)` por `decodeURIComponent(String(params.pre_nro))`. Actualizar los enlaces de `dashboard/presupuestos` y `dashboard/historico`, las mutaciones de aprobar, anular y desaprobar, y el estado del modal de PDF (`numeroDocumento`). Revisar si algún listado ordena por `pre_nro`. Verificar con `npm run build` sin errores y `npm run lint` sin errores nuevos (los 15 errores de lint existentes en esos archivos son previos a este cambio).
- [x] 5.3 Probar a mano el frontend local contra el backend de integración (tarea 2), en ambos esquemas: tablero → pendientes → detalle → histórico. Verificar que no aparece `NaN`, que el título del detalle coincide con el número clicado y que el listado alfanumérico muestra filas.

## 6. Validación en producción (manual, con datos)

- [ ] 6.1 Tras desplegar backend y frontend, regenerar las hojas de validación (1.1) y entregarlas al usuario. Verificar que el usuario confirma, en la app de los 5 tenants, que tablero, primeros pendientes y detalle coinciden con la hoja, y que en mcn el listado muestra los pendientes que indica el tablero, con el número en formato `NNNNN-AAAA-V`.
- [ ] 6.2 Si algo no coincide, hacer rollback a la imagen anterior (design.md → Migration Plan). Verificar que la app vuelve a comportarse como antes del deploy.

## 7. Documentación y cierre

- [x] 7.1 Actualizar `docs/COMPATIBILIDAD_BD_MCN.md`: columnas ya aplicadas por el cliente, `pre_nro` alfanumérico soportado por la app y PDFs de presupuestos de mcn pendientes (spec futura). Agregar en `docs/AGREGAR_TENANT.md` un gotcha: el db-check no detecta divergencias de tipo, así que hay que revisar el tipo de `pre_nro`/`ocp_nro` al dar de alta. Verificar que los enlaces del documento resuelven.
- [x] 7.2 Revisar si el flujo n8n de chat consume presupuestos y avisar que para mcn `pre_nro` llega como string (Open Question de design.md). Verificar dejando anotado el resultado en design.md.
- [x] 7.3 Correr la suite completa (`pytest`, `ruff`, `black --check`) y `openspec validate soportar-pre-nro-alfanumerico --strict`. Verificar que todo pasa sin errores antes de abrir los PR de backend y frontend. **Resultado (2026-09-30):** los 72 tests nuevos pasan. La suite heredada `tests/api` da 9 fallos y 7 errores, idénticos antes y después del cambio: son previos y requieren Postgres local con un login real. Ruff y black reportan los mismos 4 avisos y 4 archivos por formatear que en `main`, ninguno nuevo. `openspec validate --strict` pasa.
