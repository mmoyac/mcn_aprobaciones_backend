# 🔧 Ajustes requeridos en la base de datos — Tenant Maquinaria (`lexascl_mgamaq`)

**Fecha:** 2026-06-01
**Base de datos:** `lexascl_mgamaq` (servidor `179.27.152.194:3306`)
**Destinatario:** Equipo a cargo del ERP / base de datos del cliente

---

## 1. Contexto

La aplicación **MCN Aprobaciones** se conectó correctamente a la base de datos de Maquinaria. La conexión, los permisos y la mayoría de las tablas son compatibles. Sin embargo, el **módulo de Presupuestos** no puede operar todavía porque la estructura de algunas tablas de esta base difiere de la estructura esperada por la aplicación (que es la misma que ya usan los otros tenants en producción).

La aplicación identifica cada presupuesto por la **clave compuesta `(Loc_cod, pre_nro)`** y lee un conjunto fijo de columnas. En esta base, las tablas de presupuestos usan `pre_suc` en lugar de `Loc_cod` y les faltan columnas que la aplicación requiere.

> ⚠️ **Importante:** estos cambios deben aplicarse sobre la base de datos del ERP del cliente. Recomendamos respaldar las tablas afectadas antes de ejecutar cualquier `ALTER TABLE`, y validar los tipos/valores con el responsable del ERP.

---

## 2. Estado de compatibilidad

| Módulo / Tabla | Estado | Acción |
| :--- | :---: | :--- |
| Órdenes de compra (`adq004`) | ✅ Compatible | Ninguna — funciona |
| Usuarios / login (`ctbm01`) | ✅ Compatible | Ninguna |
| Proveedores (`proveea`) | ✅ Compatible | Ninguna |
| Sucursales (`loc001`) | ✅ Compatible | Ninguna |
| **Presupuestos – cabecera (`cot013`)** | ❌ Faltan columnas | Agregar 10 columnas |
| **Clientes (`clientea`)** | ❌ Faltan columnas | Agregar 17 columnas |
| **Presupuestos – ítems (`cot005`)** | ❌ Falta columna | Agregar `loc_cod` |
| **Presupuestos – costos (`cot005l`)** | ❌ Falta columna | Agregar `loc_cod` |

> El módulo de **órdenes de compra ya funciona** y puede usarse de inmediato. Lo que sigue es **solo** para habilitar el módulo de **presupuestos**.

---

## 3. Columnas a agregar

### 3.1. Tabla `cot013` (cabecera de presupuestos)

| Columna | Tipo | Nulo | Significado |
| :--- | :--- | :---: | :--- |
| `Loc_cod` | `SMALLINT` | NO | **Código de local/sucursal.** Forma parte de la clave `(Loc_cod, pre_nro)`. Debe poblarse (ver sección 4). |
| `Pre_Neto` | `BIGINT` | NO | Monto neto del presupuesto. |
| `pre_gar` | `SMALLINT` | NO | Garantía. |
| `Pre_vbggAvi` | `SMALLINT` | NO | Aviso VB Gerencia. |
| `Pre_MailEnv` | `SMALLINT` | NO | Indicador de mail enviado. |
| `Pre_MailUsu` | `CHAR(10)` | NO | Usuario que envió el email. |
| `Pre_MailFec` | `DATE` | NO | Fecha de envío de email. |
| `Pre_MailTime` | `CHAR(8)` | NO | Hora de envío de email. |
| `Pre_MailSubjet` | `TEXT` | NO | Asunto del email. |
| `Pre_MailPara` | `TEXT` | NO | Destinatarios del email. |

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

### 3.3. Tabla `cot005` (ítems del presupuesto)

| Columna | Tipo | Nulo | Significado |
| :--- | :--- | :---: | :--- |
| `loc_cod` | `SMALLINT` | NO | Código de local. Parte de la clave `(loc_cod, pre_nro)` para unir con `cot013`. Debe poblarse consistente con `cot013.Loc_cod`. |

### 3.4. Tabla `cot005l` (costos por ítem)

| Columna | Tipo | Nulo | Significado |
| :--- | :--- | :---: | :--- |
| `loc_cod` | `SMALLINT` | NO | Código de local. Igual que en `cot005`, consistente con `cot013.Loc_cod`. |

---

## 4. ⚠️ Punto crítico: poblar `Loc_cod` / `loc_cod`

No basta con **crear** las columnas; hay que **poblarlas** con datos coherentes, porque la aplicación une las tablas por la clave `(Loc_cod, pre_nro)` y muestra el nombre de la sucursal cruzando con `loc001`.

- El valor de `Loc_cod` debe corresponder a una sucursal existente en `loc001` (`loc001.Loc_cod`).
- Si en esta base la sucursal del presupuesto está hoy en `cot013.pre_suc`, lo más probable es que `Loc_cod = pre_suc`. **El equipo del ERP debe confirmar esta equivalencia.**
- El mismo `Loc_cod` debe replicarse en `cot005.loc_cod` y `cot005l.loc_cod` para cada presupuesto, de forma que coincidan por `(loc_cod, pre_nro)`.
- Los presupuestos **nuevos** que genere el ERP también deben rellenar estas columnas; de lo contrario dejarán de verse en la aplicación.

Si `Loc_cod` o `Pre_Neto` quedan vacíos o inconsistentes, los presupuestos **no aparecerán en el listado** o se mostrarán con monto/sucursal incorrectos.

---

## 5. DDL sugerido (referencia — validar antes de ejecutar)

> Estos `ALTER TABLE` son una guía. Los `DEFAULT` son para poder agregar columnas `NOT NULL` sobre filas existentes; ajusta los valores según el ERP. **Respaldar antes de ejecutar.**

```sql
-- cot013 (cabecera presupuestos)
ALTER TABLE cot013
  ADD COLUMN Loc_cod        SMALLINT     NOT NULL DEFAULT 0,
  ADD COLUMN Pre_Neto       BIGINT       NOT NULL DEFAULT 0,
  ADD COLUMN pre_gar        SMALLINT     NOT NULL DEFAULT 0,
  ADD COLUMN Pre_vbggAvi    SMALLINT     NOT NULL DEFAULT 0,
  ADD COLUMN Pre_MailEnv    SMALLINT     NOT NULL DEFAULT 0,
  ADD COLUMN Pre_MailUsu    CHAR(10)     NOT NULL DEFAULT '',
  ADD COLUMN Pre_MailFec    DATE         NOT NULL DEFAULT '1900-01-01',
  ADD COLUMN Pre_MailTime   CHAR(8)      NOT NULL DEFAULT '',
  ADD COLUMN Pre_MailSubjet TEXT         NOT NULL,
  ADD COLUMN Pre_MailPara   TEXT         NOT NULL;

-- Poblar Loc_cod desde la sucursal actual (CONFIRMAR equivalencia con el ERP)
UPDATE cot013 SET Loc_cod = pre_suc WHERE Loc_cod = 0;

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

-- cot005 (ítems) y cot005l (costos)
ALTER TABLE cot005  ADD COLUMN loc_cod SMALLINT NOT NULL DEFAULT 0;
ALTER TABLE cot005l ADD COLUMN loc_cod SMALLINT NOT NULL DEFAULT 0;

-- Poblar loc_cod en detalle a partir de la cabecera
UPDATE cot005  d JOIN cot013 c ON d.pre_nro = c.pre_nro SET d.loc_cod = c.Loc_cod;
UPDATE cot005l d JOIN cot013 c ON d.pre_nro = c.pre_nro SET d.loc_cod = c.Loc_cod;
```

---

## 6. Cómo validar que quedó correcto

Una vez aplicados los cambios, nuestro equipo puede re-ejecutar el diagnóstico automático contra la base. El indicador rápido es el endpoint:

```
GET https://api.lexastech.cl/api/v1/tenant/db-check
Header: X-Tenant-Domain: aprobaciones-mgamaq.lexastech.cl
```

Debe devolver `"tiene_errores": false`. Además validaremos por ORM que todas las columnas de `cot013` y `clientea` estén presentes (el `db-check` cubre un subconjunto; la verificación completa la hacemos nosotros).

---

## 7. Resumen ejecutivo

| Tabla | N° columnas a agregar | ¿Requiere poblar datos? |
| :--- | :---: | :--- |
| `cot013` | 10 | Sí — `Loc_cod` y `Pre_Neto` son imprescindibles |
| `clientea` | 17 | Recomendado (`Cli_NameL` al menos) |
| `cot005` | 1 (`loc_cod`) | Sí |
| `cot005l` | 1 (`loc_cod`) | Sí |

**Mientras tanto**, el módulo de **órdenes de compra está operativo** y puede comenzar a usarse sin esperar estos ajustes.
