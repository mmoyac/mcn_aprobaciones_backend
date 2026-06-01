# 🔧 Ajustes requeridos en la base de datos — Tenant MGACOM (`lexascl_mgacom`)

**Fecha:** 2026-06-01
**Base de datos:** `lexascl_mgacom` (servidor `179.27.152.194:3306`)
**Destinatario:** Equipo a cargo del ERP / base de datos del cliente

---

## 1. Contexto

La aplicación **MCN Aprobaciones** se conectó correctamente a la base de datos de MGACOM. La conexión, los permisos y la mayoría de las tablas son compatibles. El módulo de **órdenes de compra** funciona y puede usarse de inmediato.

Para habilitar el módulo de **Presupuestos** faltan unas pocas columnas en dos tablas. A diferencia de otras bases, aquí `Loc_cod`, `Pre_Neto` y las tablas de detalle ya están correctas, por lo que el ajuste es menor.

> ⚠️ **Importante:** estos cambios deben aplicarse sobre la base de datos del ERP del cliente. Recomendamos respaldar las tablas afectadas antes de ejecutar cualquier `ALTER TABLE`, y validar los tipos con el responsable del ERP.

---

## 2. Estado de compatibilidad

| Módulo / Tabla | Estado | Acción |
| :--- | :---: | :--- |
| Órdenes de compra (`adq004`) | ✅ Compatible | Ninguna — funciona |
| Usuarios / login (`ctbm01`) | ✅ Compatible | Ninguna |
| Proveedores (`proveea`) | ✅ Compatible | Ninguna |
| Sucursales (`loc001`) | ✅ Compatible | Ninguna |
| Presupuestos – ítems (`cot005`) | ✅ Compatible | Ninguna |
| Presupuestos – costos (`cot005l`) | ✅ Compatible | Ninguna |
| **Presupuestos – cabecera (`cot013`)** | ❌ Faltan columnas | Agregar 5 columnas |
| **Clientes (`clientea`)** | ❌ Faltan columnas | Agregar 17 columnas |

> El módulo de **órdenes de compra ya funciona**. Lo que sigue es **solo** para habilitar **presupuestos**.

---

## 3. Columnas a agregar

### 3.1. Tabla `cot013` (cabecera de presupuestos)

Faltan únicamente las columnas relacionadas con el envío de email:

| Columna | Tipo | Nulo | Significado |
| :--- | :--- | :---: | :--- |
| `Pre_MailUsu` | `CHAR(10)` | NO | Usuario que envió el email. |
| `Pre_MailFec` | `DATE` | NO | Fecha de envío de email. |
| `Pre_MailTime` | `CHAR(8)` | NO | Hora de envío de email. |
| `Pre_MailSubjet` | `TEXT` | NO | Asunto del email. |
| `Pre_MailPara` | `TEXT` | NO | Destinatarios del email. |

> ✅ `Loc_cod`, `Pre_Neto`, `pre_gar`, `Pre_vbggAvi` y `Pre_MailEnv` **ya existen** en esta base.

### 3.2. Tabla `clientea` (clientes)

Actualmente solo tiene `Cli_Code` y `Cli_Name`. Faltan:

| Columna | Tipo | Nulo | Significado |
| :--- | :--- | :---: | :--- |
| `Cli_Digi` | `VARCHAR(1)` | NO | Dígito verificador del RUT. |
| `cli_gircod` | `INT` | SÍ | Código de giro. |
| `Cli_NameL` | `VARCHAR(60)` | NO | Nombre largo / razón social. |
| `Ven_Cod` | `SMALLINT` | SÍ | Código de vendedor. |
| `Cli_Sele` | `VARCHAR(1)` | NO | Cliente selección. |
| `Cli_Obs` | `TEXT` | NO | Observaciones. |
| `Cli_Dcto` | `DECIMAL(4,2)` | NO | Descuento. |
| `Cli_GirDs1` | `VARCHAR(30)` | NO | Giro 1. |
| `Cli_GirDs2` | `VARCHAR(30)` | NO | Giro 2. |
| `cli_blo` | `SMALLINT` | NO | Bloqueado. |
| `Cli_PagCod` | `SMALLINT` | NO | Código de condición de pago. |
| `Cli_Est` | `SMALLINT` | NO | Estado. |
| `Cli_Cred` | `BIGINT` | NO | Crédito. |
| `Cli_Abo` | `BIGINT` | NO | Abono. |
| `Cli_Fe` | `SMALLINT` | NO | Factura electrónica. |
| `Cli_MailSII` | `VARCHAR(50)` | NO | Email SII. |
| `Cli_ExpoNro` | `VARCHAR(20)` | NO | Número de exportación. |

---

## 4. DDL sugerido (referencia — validar antes de ejecutar)

> Los `DEFAULT` son para poder agregar columnas `NOT NULL` sobre filas existentes; ajusta los valores según el ERP. **Respaldar antes de ejecutar.**

```sql
-- cot013 (cabecera presupuestos) — solo columnas de email
ALTER TABLE cot013
  ADD COLUMN Pre_MailUsu    CHAR(10)  NOT NULL DEFAULT '',
  ADD COLUMN Pre_MailFec    DATE      NOT NULL DEFAULT '1900-01-01',
  ADD COLUMN Pre_MailTime   CHAR(8)   NOT NULL DEFAULT '',
  ADD COLUMN Pre_MailSubjet TEXT      NOT NULL,
  ADD COLUMN Pre_MailPara   TEXT      NOT NULL;

-- clientea (clientes)
ALTER TABLE clientea
  ADD COLUMN Cli_Digi   VARCHAR(1)    NOT NULL DEFAULT '',
  ADD COLUMN cli_gircod INT           NULL,
  ADD COLUMN Cli_NameL  VARCHAR(60)   NOT NULL DEFAULT '',
  ADD COLUMN Ven_Cod    SMALLINT      NULL,
  ADD COLUMN Cli_Sele   VARCHAR(1)    NOT NULL DEFAULT '',
  ADD COLUMN Cli_Obs    TEXT          NOT NULL,
  ADD COLUMN Cli_Dcto   DECIMAL(4,2)  NOT NULL DEFAULT 0,
  ADD COLUMN Cli_GirDs1 VARCHAR(30)   NOT NULL DEFAULT '',
  ADD COLUMN Cli_GirDs2 VARCHAR(30)   NOT NULL DEFAULT '',
  ADD COLUMN cli_blo    SMALLINT      NOT NULL DEFAULT 0,
  ADD COLUMN Cli_PagCod SMALLINT      NOT NULL DEFAULT 0,
  ADD COLUMN Cli_Est    SMALLINT      NOT NULL DEFAULT 0,
  ADD COLUMN Cli_Cred   BIGINT        NOT NULL DEFAULT 0,
  ADD COLUMN Cli_Abo    BIGINT        NOT NULL DEFAULT 0,
  ADD COLUMN Cli_Fe     SMALLINT      NOT NULL DEFAULT 0,
  ADD COLUMN Cli_MailSII VARCHAR(50)  NOT NULL DEFAULT '',
  ADD COLUMN Cli_ExpoNro VARCHAR(20)  NOT NULL DEFAULT '';

-- Copiar nombre corto al largo si corresponde
UPDATE clientea SET Cli_NameL = Cli_Name WHERE Cli_NameL = '';
```

---

## 5. Cómo validar que quedó correcto

Una vez aplicados los cambios, nuestro equipo re-ejecuta el diagnóstico automático. Indicador rápido:

```
GET https://api.lexastech.cl/api/v1/tenant/db-check
Header: X-Tenant-Domain: aprobaciones-mgacom.lexastech.cl
```

Debe devolver `"tiene_errores": false`. Además validamos por ORM que todas las columnas de `cot013` y `clientea` estén presentes.

---

## 6. Resumen ejecutivo

| Tabla | N° columnas a agregar |
| :--- | :---: |
| `cot013` | 5 (todas de email) |
| `clientea` | 17 |

**Mientras tanto**, el módulo de **órdenes de compra está operativo** y puede comenzar a usarse sin esperar estos ajustes.
