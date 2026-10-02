# Spec Delta

## Purpose

Define cómo la app identifica, expone y recibe el número de presupuesto (`pre_nro`) de forma independiente del tipo de columna que use el ERP de cada tenant: numérico en gontec, mga, mgamaq y mgacom, y alfanumérico en mcn. Además protege las operaciones sobre los PDFs de REPPDF frente a identificadores no numéricos.

## ADDED Requirements

### Requirement: Identificador de presupuesto numérico o alfanumérico
El sistema SHALL aceptar como identificador de presupuesto (`pre_nro`) tanto un valor numérico entero como un valor de texto, según lo que almacene la base de datos del tenant, sin exigir ningún cambio de esquema en la base de datos del cliente.

#### Scenario: Tenant con pre_nro alfanumérico lista sus pendientes
- **WHEN** un usuario autenticado del tenant mcn, cuyo `pre_nro` es texto con formato `NNNNN-AAAA-V`, consulta los presupuestos pendientes
- **THEN** el sistema responde con éxito, sin error 500
- **AND** devuelve el mismo número de presupuestos que informa el indicador de pendientes del tablero
- **AND** cada presupuesto incluye su `pre_nro` exactamente como está en la base de datos (ej. `"06798-2026-0"`, conservando ceros a la izquierda y guiones)

#### Scenario: Tenant con pre_nro alfanumérico consulta aprobados e histórico
- **WHEN** un usuario del tenant mcn consulta "Aprobados Hoy" o busca en el histórico de presupuestos
- **THEN** el sistema responde con éxito e incluye el `pre_nro` alfanumérico de cada resultado

#### Scenario: Tenant con pre_nro alfanumérico ve el detalle
- **WHEN** un usuario del tenant mcn abre el detalle del presupuesto `06798-2026-0` de la sucursal correspondiente
- **THEN** el sistema devuelve las aprobaciones y los ítems de ese presupuesto, y no los de otro

### Requirement: Compatibilidad total con tenants de pre_nro numérico
Para los tenants cuyo `pre_nro` es numérico, el sistema MUST mantener sin cambios el contrato observable de la API: el campo `pre_nro` se sigue devolviendo como número JSON, y los listados, conteos, detalles y resultados de acciones son idénticos a los de la versión anterior.

#### Scenario: Mismos datos que la versión anterior para un tenant numérico
- **WHEN** se consultan indicadores, pendientes, aprobados, histórico y detalle de presupuestos de gontec, mga o mgacom con la nueva versión (mgamaq queda fuera: su módulo de presupuestos ya no funciona hoy por un esquema de BD divergente, ver `docs/COMPATIBILIDAD_BD_MAQUINARIA.md`, y debe seguir comportándose igual)
- **THEN** cada respuesta es igual a la de la versión anterior para la misma consulta y el mismo momento (mismos registros, mismos campos, mismos valores)
- **AND** `pre_nro` sigue siendo un número JSON, no un string

#### Scenario: Identificador numérico enviado como número
- **WHEN** un cliente de la API de un tenant numérico envía `pre_nro` como número (ej. `12345`) para aprobar, anular, desaprobar o ver detalle
- **THEN** el sistema opera sobre el presupuesto `12345` igual que antes

### Requirement: Acciones sobre presupuestos con identificador alfanumérico
El sistema SHALL permitir aprobar, anular y desaprobar un presupuesto identificándolo con un `pre_nro` alfanumérico, y SHALL afectar únicamente al presupuesto con ese `Loc_cod` y ese `pre_nro` exactos.

#### Scenario: Aprobar un presupuesto alfanumérico
- **WHEN** un usuario autorizado aprueba el presupuesto `Loc_cod=1, pre_nro="06798-2026-0"`
- **THEN** solo ese presupuesto queda aprobado por gerencia, con usuario, fecha y hora de la aprobación
- **AND** la respuesta devuelve `pre_nro` como `"06798-2026-0"`

#### Scenario: Anular y desaprobar un presupuesto alfanumérico
- **WHEN** un usuario autorizado anula o desaprueba un presupuesto alfanumérico
- **THEN** solo ese presupuesto cambia de estado, y ningún otro presupuesto con un número parecido (ej. `06798-2026-1`) se ve afectado

#### Scenario: Acción sobre un identificador inexistente
- **WHEN** se solicita aprobar, anular o desaprobar un `pre_nro` que no existe para ese `Loc_cod`
- **THEN** el sistema responde 404 "no encontrado", sin modificar datos y sin error 500

#### Scenario: Detalle de un identificador inexistente
- **WHEN** se solicita el detalle de un `pre_nro` que no existe para ese `Loc_cod`
- **THEN** el sistema responde igual que hoy para los tenants numéricos (200, sin ítems ni aprobaciones), sin error 500

### Requirement: Operaciones seguras sobre PDFs con identificador no numérico
Mientras el repositorio de PDFs (REPPDF) solo admita números de documento enteros, el sistema MUST NOT usar un `pre_nro` no numérico en ninguna consulta, verificación ni borrado contra ese repositorio, y SHALL informar esos presupuestos como "sin PDF". Todo valor usado contra REPPDF MUST enviarse como parámetro y nunca interpolarse en el texto de la consulta.

#### Scenario: Listado con presupuestos alfanuméricos muestra "sin PDF"
- **WHEN** se listan presupuestos de mcn
- **THEN** cada presupuesto se informa con `tienepdf = 0`
- **AND** no se ejecuta contra REPPDF ninguna consulta que contenga esos identificadores

#### Scenario: Aprobar un presupuesto alfanumérico no borra PDFs
- **WHEN** se aprueba el presupuesto `"06798-2026-0"` del tenant mcn
- **THEN** no se borra ningún registro de REPPDF, en particular no el del documento numérico `6798`

#### Scenario: Tenant numérico conserva la verificación y el borrado de PDFs
- **WHEN** se listan o se aprueban presupuestos de un tenant numérico
- **THEN** el indicador `tienepdf` y el borrado del PDF al aprobar se comportan igual que en la versión anterior

### Requirement: Frontend agnóstico al formato del identificador
La interfaz web SHALL mostrar, enlazar y operar presupuestos cuyo `pre_nro` sea numérico o alfanumérico, conservando el valor exacto recibido de la API.

#### Scenario: Navegar al detalle de un presupuesto alfanumérico
- **WHEN** un usuario de mcn hace clic en el presupuesto `#06798-2026-0` del listado de pendientes
- **THEN** se abre la página de detalle de ese presupuesto, con el número mostrado como `06798-2026-0`, sin mostrar `NaN`

#### Scenario: Filtrar por número en un tenant alfanumérico
- **WHEN** un usuario de mcn escribe `06798` en el filtro "N° presupuesto"
- **THEN** el listado muestra los presupuestos cuyo número contiene `06798`

#### Scenario: Sin regresiones visuales en tenants numéricos
- **WHEN** un usuario de gontec, mga, mgamaq o mgacom usa el tablero, pendientes, aprobados, histórico y detalle
- **THEN** ve los mismos datos y puede realizar las mismas acciones que con la versión anterior
