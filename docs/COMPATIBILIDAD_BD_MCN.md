# 🔧 Ajustes requeridos en la base de datos — Tenant MCN (`lexascl_mcn`)

**Fecha:** 2026-06-05
**Base de datos:** `lexascl_mcn` (servidor `179.27.152.194:3306`)
**Destinatario:** Equipo a cargo del ERP / base de datos del cliente

---

## 1. Contexto

La aplicación **MCN Aprobaciones** se conectó correctamente a la base de datos de MCN (159 tablas). La conexión y los permisos funcionan.

A diferencia de otros tenants, en MCN faltan columnas que afectan **también al módulo de órdenes de compra** (no solo presupuestos). Por eso, aunque el tablero muestra el contador de órdenes, **el listado y el detalle de órdenes no se ven** hasta aplicar los ajustes de la sección 3.1.

> ⚠️ **Importante:** estos cambios deben aplicarse sobre la base de datos del ERP del cliente. Recomendamos respaldar las tablas afectadas antes de ejecutar cualquier `ALTER TABLE`, y validar los tipos con el responsable del ERP.

---

## 2. Estado de compatibilidad

| Módulo / Tabla | Estado | Acción |
| :--- | :---: | :--- |
| Usuarios / login (`ctbm01`) | ✅ Compatible | Ninguna |
| Proveedores (`proveea`) | ✅ Compatible | Ninguna |
| Sucursales (`loc001`) | ✅ Compatible | Ninguna |
| **Órdenes de compra – cabecera (`adq004`)** | ❌ Faltan columnas | Agregar 4 columnas (nivel A4) |
| **Órdenes de compra – ítems (`adq005`)** | ❌ Falta columna | Agregar `Loc_cod` |
| **Presupuestos – cabecera (`cot013`)** | ❌ Faltan columnas | Agregar 20 columnas |
| **Presupuestos – ítems (`cot005`)** | ❌ Falta columna | Agregar `loc_cod` |
| **Presupuestos – costos (`cot005l`)** | ❌ Falta columna | Agregar `loc_cod` |
| **Clientes (`clientea`)** | ❌ Faltan columnas | Agregar 17 columnas |

> **Prioridad:** la sección **3.1 (órdenes de compra)** es lo mínimo para dejar operativo el módulo principal. La sección **3.2 (presupuestos)** habilita el segundo módulo.

---

## 3. Columnas a agregar

### 3.1. Órdenes de compra (prioritario)

**`adq004`** — faltan las 4 columnas del nivel de aprobación 4 (A4):

| Columna | Tipo | Nulo | Significado |
| :--- | :--- | :---: | :--- |
| `ocp_A4_Ap` | `SMALLINT` | NO | Aprobación nivel 4 (0/1). |
| `ocp_A4_Dt` | `DATE` | SÍ | Fecha aprobación nivel 4. |
| `ocp_A4_Hr` | `VARCHAR(8)` | NO | Hora aprobación nivel 4. |
| `ocp_A4_Usu` | `VARCHAR(10)` | NO | Usuario aprobación nivel 4. |

**`adq005`** — falta la columna de sucursal (parte de la clave del ítem):

| Columna | Tipo | Nulo | Significado |
| :--- | :--- | :---: | :--- |
| `Loc_cod` | `SMALLINT` | NO | Código de sucursal (debe poblarse acorde a la cabecera `adq004`). |

### 3.2. Presupuestos

**`cot013`** (cabecera) — faltan 20 columnas:

| Columna | Tipo | Nulo | | Columna | Tipo | Nulo |
| :--- | :--- | :---: | :--- | :--- | :--- | :---: |
| `Loc_cod` | `SMALLINT` | NO | | `pre_vbggUsu` | `CHAR(10)` | NO |
| `pre_gar` | `SMALLINT` | NO | | `pre_vbggDt` | `DATE` | NO |
| `Pre_vbLib` | `SMALLINT` | NO | | `pre_vbggTime` | `CHAR(8)` | NO |
| `Pre_VbLibUsu` | `CHAR(10)` | NO | | `Pre_vbggAvi` | `SMALLINT` | NO |
| `Pre_VBLibDt` | `DATE` | NO | | `Pre_MailEnv` | `SMALLINT` | NO |
| `Pre_VbLibTime` | `CHAR(8)` | NO | | `Pre_Neto` | `BIGINT` | NO |
| `pre_VbUsu` | `CHAR(10)` | NO | | `Pre_MailUsu` | `CHAR(10)` | NO |
| `pre_VbFec` | `DATE` | NO | | `Pre_MailFec` | `DATE` | NO |
| `pre_vbgg` | `SMALLINT` | NO | | `Pre_MailTime` | `CHAR(8)` | NO |
| | | | | `Pre_MailSubjet` | `TEXT` | NO |
| | | | | `Pre_MailPara` | `TEXT` | NO |

**`cot005`** y **`cot005l`** (detalle) — falta `loc_cod` (`SMALLINT NOT NULL`) en ambas.

**`clientea`** (clientes) — faltan las mismas 17 columnas que en los otros tenants (ver [COMPATIBILIDAD_BD_MGACOM.md §3.2](COMPATIBILIDAD_BD_MGACOM.md)).

---

## 4. DDL sugerido (referencia — validar antes de ejecutar)

> Los `DEFAULT` permiten agregar columnas `NOT NULL` sobre filas existentes; ajusta los valores según el ERP. **Respaldar antes de ejecutar.**

```sql
-- ===== ÓRDENES DE COMPRA (prioritario) =====
ALTER TABLE adq004
  ADD COLUMN ocp_A4_Ap  SMALLINT    NOT NULL DEFAULT 0,
  ADD COLUMN ocp_A4_Dt  DATE        NULL,
  ADD COLUMN ocp_A4_Hr  VARCHAR(8)  NOT NULL DEFAULT '',
  ADD COLUMN ocp_A4_Usu VARCHAR(10) NOT NULL DEFAULT '';

-- adq005: agregar Loc_cod y poblarlo desde la cabecera adq004
ALTER TABLE adq005
  ADD COLUMN Loc_cod SMALLINT NOT NULL DEFAULT 0;
UPDATE adq005 d
  JOIN adq004 c ON c.ocp_nro = d.ocp_nro
  SET d.Loc_cod = c.Loc_cod;

-- ===== PRESUPUESTOS =====
ALTER TABLE cot013
  ADD COLUMN Loc_cod        SMALLINT NOT NULL DEFAULT 0,
  ADD COLUMN pre_gar        SMALLINT NOT NULL DEFAULT 0,
  ADD COLUMN Pre_vbLib      SMALLINT NOT NULL DEFAULT 0,
  ADD COLUMN Pre_VbLibUsu   CHAR(10) NOT NULL DEFAULT '',
  ADD COLUMN Pre_VBLibDt    DATE     NOT NULL DEFAULT '1900-01-01',
  ADD COLUMN Pre_VbLibTime  CHAR(8)  NOT NULL DEFAULT '',
  ADD COLUMN pre_VbUsu      CHAR(10) NOT NULL DEFAULT '',
  ADD COLUMN pre_VbFec      DATE     NOT NULL DEFAULT '1900-01-01',
  ADD COLUMN pre_vbgg       SMALLINT NOT NULL DEFAULT 0,
  ADD COLUMN pre_vbggUsu    CHAR(10) NOT NULL DEFAULT '',
  ADD COLUMN pre_vbggDt     DATE     NOT NULL DEFAULT '1900-01-01',
  ADD COLUMN pre_vbggTime   CHAR(8)  NOT NULL DEFAULT '',
  ADD COLUMN Pre_vbggAvi    SMALLINT NOT NULL DEFAULT 0,
  ADD COLUMN Pre_MailEnv    SMALLINT NOT NULL DEFAULT 0,
  ADD COLUMN Pre_Neto       BIGINT   NOT NULL DEFAULT 0,
  ADD COLUMN Pre_MailUsu    CHAR(10) NOT NULL DEFAULT '',
  ADD COLUMN Pre_MailFec    DATE     NOT NULL DEFAULT '1900-01-01',
  ADD COLUMN Pre_MailTime   CHAR(8)  NOT NULL DEFAULT '',
  ADD COLUMN Pre_MailSubjet TEXT     NOT NULL,
  ADD COLUMN Pre_MailPara   TEXT     NOT NULL;

-- cot005 / cot005l: agregar loc_cod
ALTER TABLE cot005  ADD COLUMN loc_cod SMALLINT NOT NULL DEFAULT 0;
ALTER TABLE cot005l ADD COLUMN loc_cod SMALLINT NOT NULL DEFAULT 0;

-- clientea: ver DDL en COMPATIBILIDAD_BD_MGACOM.md (sección 4)
```

> ⚠️ El `Loc_cod`/`loc_cod` es parte de la **clave** que la app usa para identificar órdenes y presupuestos por sucursal. Debe quedar **poblado con el valor correcto de sucursal**, no en `0`. Confirmar con el responsable del ERP cómo derivarlo.

---

## 5. Cómo validar que quedó correcto

Una vez aplicados los cambios, nuestro equipo re-ejecuta el diagnóstico automático:

```
GET https://api.lexastech.cl/api/v1/tenant/db-check
Header: X-Tenant-Domain: aprobaciones-mcn.lexastech.cl
```

Debe devolver `"tiene_errores": false`. El diagnóstico valida todas las columnas que la app realmente usa (derivadas del modelo ORM + tablas de SQL crudo; ver [SPEC-001](specs/SPEC-001-deteccion-incompatibilidad-bd.md)).

---

## 6. Resumen ejecutivo

| Módulo | Tabla | N° columnas a agregar |
| :--- | :--- | :---: |
| **Órdenes (prioritario)** | `adq004` | 4 (nivel A4) |
| **Órdenes (prioritario)** | `adq005` | 1 (`Loc_cod`) |
| Presupuestos | `cot013` | 20 |
| Presupuestos | `cot005` | 1 (`loc_cod`) |
| Presupuestos | `cot005l` | 1 (`loc_cod`) |
| Presupuestos | `clientea` | 17 |

**Con solo las 5 columnas de la sección 3.1**, el módulo de **órdenes de compra** queda operativo.
