# SPEC-002 — Degradación con gracia ante BD del tenant incompleta

| | |
| :--- | :--- |
| **Estado** | 🟡 Propuesta (pendiente de priorización) |
| **Fecha** | 2026-06-05 |
| **Autor** | mmoyac |
| **Componentes** | Backend endpoints de órdenes/presupuestos · Frontend dashboard |
| **Relacionado** | [SPEC-001](SPEC-001-deteccion-incompatibilidad-bd.md) (detección) · [docs/AGREGAR_TENANT.md](../AGREGAR_TENANT.md) |

---

## 1. Contexto y problema

Cuando la BD MySQL de un tenant está incompleta (le faltan columnas que el ORM exige), los endpoints de datos (`/ordenes-compra/*`, `/presupuestos/*`) **revientan con HTTP 500** crudo, porque la query hace `SELECT` de columnas inexistentes (ej. `Unknown column 'adq004.ocp_A4_Ap'`).

Esto produce, en el dashboard del tenant afectado (caso real: `mcn`):
- Secciones que fallan con 500 → el frontend reintenta (mitigado en SPEC-001/retry, pero sigue mostrando error abrupto).
- Mala experiencia: el usuario ve errores rotos en vez de un mensaje claro de "este módulo no está disponible hasta completar la BD".

[SPEC-001](SPEC-001-deteccion-incompatibilidad-bd.md) ya resolvió la **detección** (el panel del tablero lista qué falta). SPEC-002 aborda la **degradación**: que la app no se rompa, sino que informe con gracia.

---

## 2. Objetivos y no-objetivos

### Objetivos
1. Que los endpoints de datos **no devuelvan 500** cuando la causa es una columna/tabla faltante en la BD del tenant.
2. Devolver una respuesta **estructurada** que el frontend pueda interpretar para mostrar un estado "módulo no disponible — BD incompleta" en vez de un error genérico.
3. Mantener el comportamiento normal intacto para tenants con BD completa.

### No-objetivos
- No se corrige la BD del cliente (eso lo hace el cliente; SPEC-001 ya documenta qué falta).
- No se cambia la lógica de negocio de órdenes/presupuestos.
- No se re-implementa la detección (ya está en `/tenant/db-check`).

---

## 3. Alcance

| Dentro | Fuera |
| :--- | :--- |
| Manejo de `OperationalError` (1054 columna desconocida, 1146 tabla inexistente) en endpoints de datos | Validación previa de cada request contra el schema |
| Respuesta degradada (HTTP 200 con flag, o 422 estructurado) | Cambiar el panel `DbHealthAlert` (ya cumple su rol) |
| Estado visual "módulo no disponible" en el frontend | Reintentos de React Query (ya ajustado en SPEC-001) |

---

## 4. Diseño propuesto (alternativas a evaluar)

### Opción A — Manejo de excepción por endpoint
Capturar `sqlalchemy.exc.OperationalError` (códigos 1054/1146) en los services/endpoints de órdenes y presupuestos, y devolver una respuesta estructurada:

```json
{ "disponible": false, "motivo": "bd_incompleta", "detalle": "Unknown column 'adq004.ocp_A4_Ap'" }
```

con HTTP 200 (o 422). El frontend, al ver `disponible: false`, muestra un cartel "Módulo no disponible — la base de datos del cliente requiere ajustes (ver tablero)".

- ➕ Acotado, no toca la query feliz.
- ➖ Hay que envolver varios endpoints; el `detalle` expone nombres internos (mostrar genérico al usuario).

### Opción B — Middleware/handler global
Un *exception handler* de FastAPI para `OperationalError` que detecte 1054/1146 y devuelva el cuerpo degradado de forma centralizada.

- ➕ Un solo punto, cubre todos los endpoints presentes y futuros.
- ➖ Menos contexto sobre qué módulo falló; hay que mapear el error a una respuesta consistente.

### Opción C — Pre-chequeo por dependencia
Un `Depends` que, para los routers de datos, consulte el resultado de `build_required_schema()` vs la BD (cacheado) y corte temprano con un 422 estructurado si la tabla de ese módulo está incompleta.

- ➕ No depende de atrapar la excepción; falla rápido y explícito.
- ➖ Costo de validación por request (mitigable con caché por tenant).

> **Recomendación inicial:** Opción B (handler global) para 500→respuesta estructurada uniforme, complementada con un mensaje claro en el frontend. Evaluar caché de compatibilidad por tenant si se quiere fallar antes (C).

---

## 5. Criterios de aceptación (borrador)

- **CA-1.** En un tenant con BD incompleta, `GET /ordenes-compra/pendientes` devuelve una respuesta estructurada (no 500) que el frontend interpreta.
- **CA-2.** El dashboard muestra, en la sección afectada, un mensaje "módulo no disponible por BD incompleta" en vez de un error genérico o spinner colgado.
- **CA-3.** En un tenant con BD completa (`mga`), el comportamiento y los tiempos no cambian.
- **CA-4.** El mensaje al usuario final no expone nombres de columnas/tablas internos (eso queda en el tablero técnico / logs).

## 6. Notas de implementación

- Mitigación parcial ya aplicada (SPEC-001): el `QueryClient` del frontend bajó a `retry: 1` para no colgar el dashboard ~7 s ante un 500.
- Reutilizar la detección de SPEC-001 (`build_required_schema` + `/tenant/db-check`) para no duplicar la lógica de "qué falta".

## 7. Pendiente

- Decidir Opción A/B/C.
- Definir contrato exacto de la respuesta degradada con el frontend.
- Estimar y priorizar.
