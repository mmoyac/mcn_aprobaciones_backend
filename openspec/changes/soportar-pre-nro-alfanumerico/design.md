# Design

## Context

La motivación está en proposal.md (sección Why) y los requisitos en `specs/presupuestos/identificador-presupuesto/spec.md`. Estado actual relevante:

- **Modelo:** `Presupuesto.pre_nro` está declarado `BigInteger` (`app/models/presupuesto.py`). No se generan tablas desde el ORM (las BD son del ERP), así que el tipo del modelo solo afecta el bind/lectura, no el DDL. Con pymysql, la columna `char(12)` de mcn ya llega como `str`: los logs de prod lo confirman, porque la consulta se ejecuta y falla después.
- **Schemas Pydantic (v2.5):** `pre_nro: int` en `PresupuestoBase`, `PresupuestoAprobar`, `PresupuestoAprobadoResponse`, en el schema de anular/desaprobar (`app/schemas/presupuesto.py`) y en `DetallePresupuesto`/`PresupuestoHistorico` (`app/schemas/presupuesto_detalle.py`). Aquí nace el 500.
- **Endpoints:** `GET /presupuestos/{loc_cod}/{pre_nro}/detalle` tipa `pre_nro: int`. Aprobar, anular y desaprobar reciben `pre_nro` en el body.
- **SQL crudo:** el detalle (`cot012`, `cot005`, `cot005l`) y el histórico ya usan parámetros enlazados, así que funcionan con ambos tipos.
- **REPPDF (`pdf001.PdfNumero BIGINT`):**
  - `_verificar_pdfs_batch` interpola `IN (…)` con `str(n)`, sin comillas ni parámetros.
  - `_eliminar_pdf_reppdf` compara `PdfNumero = :numero`: con `'06798-2026-0'`, MySQL lo convierte a `6798`.
- **Frontend:** `pre_nro: number` en `lib/types/index.ts` y en las páginas. El detalle hace `Number(params.pre_nro)`. Los PDF solo se ofrecen si `tienepdf` es 1 o 2.
- **Autenticación:** JWT firmado con `SECRET_KEY`. `get_current_user` busca al usuario en la BD del tenant (`ctbm01`).
- **Tests actuales:** 4 archivos pequeños en `tests/api`; no hay tests de presupuestos contra una BD con datos.

- **Hallazgo en la tarea 1.2 (2026-09-30):** de los 4 tenants numéricos, solo **gontec, mga y mgacom** tienen presupuestos operativos. En mgamaq, `cot013` no tiene `Loc_cod` ni otras 9 columnas, y `clientea`/`cot005`/`cot005l` también divergen. Ya estaba documentado en `docs/COMPATIBILIDAD_BD_MAQUINARIA.md` y queda fuera de este cambio. La referencia de "sin regresión" para presupuestos son esos 3 tenants; para mgamaq solo se verifica que no cambie su comportamiento.

## Goals / Non-Goals

**Goals:**
- Un único camino de código para ambos formatos de `pre_nro`, sin ramas por tenant ni configuración por tenant.
- Cero diferencias observables para los tenants numéricos, verificado con tests de integración locales y corroborado por el usuario con hojas de datos por tenant.
- Cero escrituras en BD productivas durante las pruebas; en prod, solo lecturas para generar los datos de validación.

**Non-Goals:**
- Normalizar o reformatear el `pre_nro` de mcn: se muestra tal como viene.
- Detectar el tipo de columna por tenant (introspección o configuración): no hace falta si el código es agnóstico.
- Cambiar el endpoint `documentos-pdf/get-cliente` (`numero: int`): con `tienepdf = 0` el frontend nunca lo llama para mcn.

## Decisions

### D1. Tipo en la API: `Union[int, str]` (int primero), no `str` para todos
- **Qué:** en los schemas, `pre_nro: Union[int, str]`. En modo `smart` de Pydantic v2 se conserva el tipo exacto de entrada:
  - un `int` que viene de un `BIGINT` se serializa como número JSON;
  - un `str` que viene de un `char` se serializa como string, sin intentar convertir `"06798-2026-0"`.
- **Por qué:** cumple el requisito de compatibilidad total. Los tenants numéricos siguen recibiendo números, y los consumidores externos (flujo n8n, frontend actual) no notan nada.
- **Alternativa descartada:** `str` para todos. Es más simple, pero cambia el JSON de los 4 tenants sanos (`12345` → `"12345"`) y podría romper el flujo n8n y el ordenamiento o las comparaciones del frontend.
- **Cuidado:** en bodies de entrada (aprobar, anular, desaprobar) un cliente de un tenant numérico podría mandar `"12345"` como string. Se deja como `str`; MySQL compara `BIGINT = '12345'` correctamente. Se agrega un test para este caso.

### D2. Parámetro de ruta del detalle: `str`
- **Qué:** `pre_nro: str` en la ruta, pasado tal cual a los parámetros enlazados.
- **Por qué:** en la ruta todo llega como texto. `BIGINT = '12345'` funciona en MySQL y `char(12) = '06798-2026-0'` es comparación exacta. No hace falta convertir a int.
- **Validación:** longitud máxima de 20 caracteres y patrón `^[0-9A-Za-z\-]+$`, para rechazar basura con 422 antes de llegar a la BD.

### D3. Modelo ORM: columna `pre_nro` con un tipo que no transforme valores
- **Qué:** declarar `pre_nro` como `String(20)`. No se emite DDL, porque el ORM nunca crea estas tablas.
- **Efecto al leer:** pymysql entrega `int` para columnas `BIGINT` y `str` para `char`, y `String` no aplica conversión en lectura. El valor llega tal cual al schema (D1).
- **Efecto al escribir:** los filtros `Presupuesto.pre_nro == valor` envían el valor recibido.
- **Verificación:** hay un test que comprueba que, con `String`, una columna `BIGINT` sigue llegando como `int`. Si el driver no se comportara así, la alternativa es un `TypeDecorator` que convierta a `int` todo valor puramente numérico. Queda como plan B, no por defecto, porque cambiaría `"00123"` si alguna vez existiera.
- **db-check:** el db-check deriva las columnas del ORM (SPEC-001) y no compara tipos, así que no le afecta.

### D4. REPPDF: filtrar identificadores no numéricos y usar parámetros
- **Qué:** una función única `_es_numero_reppdf(v)` que responde verdadero solo si es un `int`, o un `str` de solo dígitos (sin signo) que cabe en `BIGINT`.
- **Verificación en lote:** solo se consultan los números numéricos, con parámetros enlazados (`IN :numeros` con `bindparam(expanding=True)`). Los demás se marcan `tienepdf = 0` sin tocar REPPDF.
- **Borrado al aprobar:** si el número no es numérico, se omite el borrado y se deja un log.
- **Clave del mapa:** `pdf_map` normaliza la clave a `(loc_cod, int(numero))` para los numéricos, así se mantiene el comportamiento actual.
- **Por qué:** cierra dos errores latentes (interpolación sin comillas y conversión implícita de MySQL) y cumple el requisito de "operaciones seguras sobre PDFs".

### D5. Frontend: `number | string` y sin conversiones numéricas
- **Qué:**
  - `pre_nro: number | string` en los tipos y firmas (`getDetalle`, `getPDF`, mutaciones, estado del modal de PDF).
  - La página de detalle usa `decodeURIComponent(params.pre_nro)` en vez de `Number(...)`.
  - Los enlaces usan `encodeURIComponent(String(pre_nro))`.
  - El filtro ya usa `String(p.pre_nro)`, así que no cambia.
  - `numeroDocumento={pdfModal.pre_nro || 0}` se adapta al tipo del componente visor.
- **Dónde:** repo `mcn_aprobaciones_frontend`, rama `feat/pre-nro-alfanumerico`.

### D6. Estrategia de pruebas (tres capas, sin escrituras en prod)
1. **Unitarias:** `_es_numero_reppdf`; serialización de los schemas (`12345` → número, `"06798-2026-0"` → string, `"00123"` → string); validación del parámetro de ruta.
2. **Integración con BD real local (lectura y escritura):**
   - Se levanta un MySQL 5.7 en Docker (`docker-compose.test.yml`) con dos esquemas generados desde `schema/db_tables.sql`: uno con `pre_nro BIGINT` y otro con `char(12)`, más un esquema REPPDF de prueba.
   - Se cargan datos semilla con casos límite: `06798-2026-0` y `06798-2026-1` (misma base, distinto sufijo), y un PDF numérico `6798` para probar que no se borra.
   - Se ejecuta la API completa con `TestClient`, con `get_tenant_db` y la sesión REPPDF apuntando a ese MySQL, y un JWT emitido en el test.
   - Cubre los requisitos de acciones y de PDFs, incluido aprobar, anular y desaprobar.
3. **Validación manual guiada por datos (sin infraestructura E2E):**
   - Antes del deploy, un script de solo lectura (`scripts/datos_validacion.py`) consulta directamente las BD de los 5 tenants (`SELECT` únicamente) y genera, por tenant, una hoja de validación con:
     - la cantidad de pendientes y de aprobados hoy (los números del tablero);
     - los 5 primeros pendientes (número, fecha, cliente, neto) en el orden del listado;
     - para 1 presupuesto por tenant, sus ítems y su estado de aprobaciones (lo que debe verse en el detalle).
   - El usuario corrobora esos datos en la app **actual** de los 4 tenants numéricos (debe coincidir ya hoy) y, después del deploy, repite la revisión en los 5 tenants. Para mcn, el listado debe dejar de salir vacío y coincidir con la hoja.
   - La hoja se regenera justo antes de cada revisión, porque entran presupuestos nuevos.
   - La cobertura de escrituras (aprobar, anular, desaprobar, PDFs) la dan los tests de integración locales (D6.2); en prod no se ejecuta ninguna acción de escritura como prueba.

## Risks / Trade-offs

- **[Pydantic convierte `"123"` a `123`, o `123` a `"123"`]** → Modo `smart` con `int` primero conserva el tipo exacto. Lo cubren los tests unitarios de D6.1; si fallan, se usa `Union[StrictInt, StrictStr]`.
- **[Otro consumidor de la API asume que `pre_nro` es número también en mcn]** → Hoy mcn no funciona, así que nadie depende de ese dato. Se documenta en OpenAPI y se revisa el flujo n8n antes del deploy (tarea explícita).
- **[La validación en prod es manual]** → Se compensa con los tests de integración locales, que cubren ambos tipos de `pre_nro` y todas las escrituras, y con hojas de datos concretas que dejan poco margen de interpretación. Si algo no coincide tras el deploy, el rollback es inmediato (sin migraciones).
- **[Los PDFs de mcn quedan sin soporte]** → Aceptado y fuera de alcance. Se mostrarán como "sin PDF", igual que hoy.
- **[Ordenamiento]** → Los listados ordenan por fecha, no por `pre_nro`, así que no hay cambio. Si el frontend ordenara por número, un `string` ordena de forma lexicográfica; se revisa en la tarea de frontend.

## Migration Plan

1. Merge de backend y frontend en sus ramas; se despliegan juntos: primero el backend, que es compatible hacia atrás con el frontend actual, y después el frontend.
2. El deploy del backend sigue `docs/DEPLOY_VPS.md` (CI; si falla el SCP, deploy manual).
3. Verificación post-deploy: se regenera la hoja de validación y el usuario revisa los 5 tenants en la app.
4. **Rollback:** volver a la imagen anterior de Docker Hub (tag previo) y al build anterior del frontend. Sin migraciones de BD, el rollback es inmediato.

## Open Questions

- ~~¿El flujo n8n de chat consulta presupuestos de mcn?~~ **Resuelto (tarea 7.2, 2026-09-30):** el flujo `ZvDpxJjJwjBTUO8A` llama a `GET /presupuestos/pendientes`, pero solo para mga, gontec, mgacom y mgamaq; mcn no está configurado. Esos tenants siguen recibiendo `pre_nro` numérico (D1), así que no hay impacto. Si se agrega mcn, el agente recibirá `pre_nro` como texto (`"06798-2026-0"`), lo que no requiere cambios porque el modelo lo trata como texto.
