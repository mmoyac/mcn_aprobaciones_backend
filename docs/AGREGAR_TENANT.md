# ➕ Agregar un Tenant Nuevo (Producción) — Runbook

Procedimiento **probado en producción** para dar de alta un nuevo tenant (empresa/cliente) en el sistema MCN Aprobaciones. Incluye los comandos exactos, los scripts de verificación y los problemas reales encontrados (ver [§9 Lecciones aprendidas](#9-lecciones-aprendidas--gotchas)).

> **Para la IA / quien ejecute:** este runbook se validó dando de alta `mgamaq` y `mgacom` el 2026-06-01. Seguí los pasos en orden; cada paso tiene un comando de verificación. No saltees la verificación de conexión (paso 3) — el error más común es un espacio sobrante en `db_name`.

---

## Arquitectura (contexto mínimo)

- Los tenants viven en **PostgreSQL** (contenedor `mcn_postgres`).
- El [`TenantMiddleware`](../app/core/tenant_middleware.py) resuelve el tenant en cada request por **dominio**, con esta prioridad de headers: `X-Tenant-Domain` → `Origin` → `Referer` → `Host`.
- El **frontend** (`mcn_frontend`, contenedor único compartido) es **multi-tenant dinámico**: envía `X-Tenant-Domain: window.location.hostname` en cada request ([client.ts](../../mcn_aprobaciones_frontend/lib/api/client.ts)). **No requiere cambios para un tenant nuevo.**
- Cada tenant apunta a su propia **base de datos MySQL de negocio** (el ERP del cliente).
- El **backend** (`api.lexastech.cl`) y el **frontend** son compartidos; lo único por-tenant en infraestructura es el **subdominio del frontend** (`aprobaciones-<slug>.lexastech.cl`).

### Modelo de datos (PostgreSQL)

| Tabla | Para qué | Campos |
| :--- | :--- | :--- |
| `tenant_temas` | Paleta de colores (maestra, **reutilizable**; usar `tema_id = 1` por defecto) | `nombre`, `color_*` |
| `tenants` | Registro de la empresa | `slug` (único), `nombre`, `dominio` (único), `tema_id` (FK), `logo_url` (opcional), `activo` |
| `tenant_conexiones` | Credenciales MySQL del tenant | `tenant_id` (FK, único), `db_host`, `db_port`, `db_name`, `db_user`, `db_password` |

---

## 📋 Resumen de pasos

| # | Paso | Dónde |
| :-: | :--- | :--- |
| 1 | Recopilar datos + crear registros en PostgreSQL | VPS / psql |
| 2 | Configurar DNS en Cloudflare (**DNS-only / nube gris**) | Cloudflare |
| 3 | **Verificar conexión MySQL** (limpia espacios) | VPS / `docker exec` |
| 4 | Verificar compatibilidad de schema (ORM vs BD real) | VPS / `docker exec` |
| 5 | Emitir certificado SSL (webroot + ecdsa) | VPS / certbot |
| 6 | Configurar nginx (`cp` + `sed` de un conf existente) | VPS |
| 7 | Verificación final (curl + endpoints) | VPS |
| 8 | Documentar ajustes de BD pendientes para el cliente | docs/ |

> **Variables que uso en los ejemplos:** `<slug>` (ej. `mgacom`), `<dominio>` = `aprobaciones-<slug>.lexastech.cl`.

---

## 1. Datos del tenant + registros en PostgreSQL

### 1.1. Datos a recopilar

- **slug**, **nombre** (visible en el front), **dominio** (`aprobaciones-<slug>.lexastech.cl`), **logo_url** (opcional)
- **Credenciales MySQL** del ERP: `db_host`, `db_port` (3306), `db_name`, `db_user`, `db_password`

> 💡 Los tenants de la familia MGA (`mga`, `mgamaq`, `mgacom`) comparten servidor `179.27.152.194:3306` y usuario `lexascl_mgaadm`. Otros tenants pueden estar en otro servidor (ej. `gontec` → `179.27.210.204`). Confirmar siempre.

### 1.2. Insertar en PostgreSQL

```bash
docker exec -it mcn_postgres psql -U <usuario_pg> -d <db_pg>
```

```sql
-- Reutiliza el tema 1 salvo que el cliente quiera colores propios
INSERT INTO tenants (slug, nombre, dominio, tema_id, logo_url, activo)
VALUES ('<slug>', 'Nombre Visible', 'aprobaciones-<slug>.lexastech.cl', 1, NULL, true)
RETURNING id;

INSERT INTO tenant_conexiones (tenant_id, db_host, db_port, db_name, db_user, db_password)
VALUES (<id_anterior>, '179.27.x.x', 3306, 'lexascl_xxx', 'usuario', 'password');
```

> ⚠️ **Cuidado al pegar `db_name`**: si queda con un espacio al final (`'lexascl_xxx '`) la conexión falla con `Incorrect database name`. El paso 3 lo limpia automáticamente, pero conviene pegarlo bien.

---

## 2. DNS en Cloudflare

El subdominio debe resolver al VPS (`168.231.96.205`) en modo **DNS-only (nube gris ⚪)**, igual que los demás `aprobaciones-*`.

- Cloudflare → DNS → registro `A` `aprobaciones-<slug>` → valor `168.231.96.205` → **nube GRIS** (no naranja).
- ⚠️ **Si queda proxied (naranja 🟠)** resuelve a IPs de Cloudflare (`104.21.x` / `172.67.x`) y el challenge webroot del cert se complica + queda inconsistente con el resto.

### Verificar (desde cualquier máquina)

El caché DNS local miente; consultá a un resolver público:

```powershell
# Windows PowerShell
Clear-DnsClientCache
Resolve-DnsName aprobaciones-<slug>.lexastech.cl -Type A -Server 1.1.1.1
```
```bash
# Linux
dig +short aprobaciones-<slug>.lexastech.cl @1.1.1.1
```

Debe devolver **`168.231.96.205`** (no IPs de Cloudflare).

---

## 3. ✅ Verificar conexión MySQL (paso crítico)

Este script valida el slug/dominio, **limpia espacios sobrantes** en `db_name`/`db_user`/`db_host` (causa #1 de fallos) y prueba la conexión real. Reemplazá `<slug>`:

```bash
docker exec -i mcn_backend python <<'PY'
from app.db.session_postgres import SessionPostgres
from app.models.tenant import Tenant
from app.db.tenant_session import create_tenant_session
from sqlalchemy import text

SLUG = '<slug>'   # <-- cambiar
db = SessionPostgres()
t = db.query(Tenant).filter(Tenant.slug == SLUG).first()
if not t:
    print(f"NO existe tenant slug={SLUG!r} (revisar el INSERT)")
else:
    print(f"tenant: nombre={t.nombre!r} dominio={t.dominio!r} activo={t.activo} tema_id={t.tema_id}")
    c = t.conexion
    if not c:
        print("Tenant SIN fila en tenant_conexiones")
    else:
        print(f"host={c.db_host!r} port={c.db_port} db={c.db_name!r} user={c.db_user!r} pass_len={len(c.db_password or '')}")
        c.db_name = (c.db_name or '').strip()
        c.db_user = (c.db_user or '').strip()
        c.db_host = (c.db_host or '').strip()
        db.commit()
        try:
            s = create_tenant_session(c.db_host, c.db_port, c.db_name, c.db_user, c.db_password)
            n = len(s.execute(text("SHOW TABLES")).fetchall())
            print(f"CONEXION OK - {n} tablas")
            s.close()
        except Exception as e:
            print("ERROR MySQL:", repr(e))
db.close()
PY
```

**Interpretar el resultado:**
- `CONEXION OK - N tablas` → seguir.
- `Access denied for user 'x'@'168.231.96.205'` → falta `GRANT` en el servidor MySQL del cliente para la IP del VPS (`168.231.96.205`). Pedirlo al cliente.
- `Incorrect database name` / `Unknown database` → `db_name` mal (el script ya hizo `.strip()`; si persiste, el nombre es incorrecto).
- `Can't connect` / timeout → host/puerto mal o firewall.

---

## 4. Verificar compatibilidad de schema (ORM vs BD real)

El endpoint `/tenant/db-check` solo valida un **subconjunto** de columnas. La verificación **autoritativa** compara cada modelo ORM contra la BD real, porque `db.query(Presupuesto)` hace `SELECT` de **todas** las columnas mapeadas (incluida la relación `cliente` lazy=joined sobre `clientea`): cualquiera ausente rompe la query.

```bash
docker exec -i mcn_backend python <<'PY'
import app.models  # registra todos los modelos
from app.db.session_postgres import SessionPostgres
from app.models.tenant import Tenant
from app.db.tenant_session import create_tenant_session
from app.db.base_class import Base
from sqlalchemy import text

SLUG = '<slug>'   # <-- cambiar
db = SessionPostgres()
t = db.query(Tenant).filter(Tenant.slug == SLUG).first()
c = t.conexion
s = create_tenant_session(c.db_host, c.db_port, c.db_name, c.db_user, c.db_password)

MYSQL_TABLES = {'cot013', 'adq004', 'loc001', 'clientea', 'proveea', 'ctbm01'}

def live_cols(tabla):
    try:
        return {r[0].lower() for r in s.execute(text(f"DESCRIBE `{tabla}`")).fetchall()}, None
    except Exception as e:
        return None, str(e).splitlines()[0]

print("===== MODELOS ORM vs BASE =====")
for mapper in Base.registry.mappers:
    tabla = mapper.local_table.name
    if tabla not in MYSQL_TABLES:
        continue
    model_cols = [col.name for col in mapper.columns]
    live, err = live_cols(tabla)
    if live is None:
        print(f"[{tabla}] NO EXISTE ({err})"); continue
    missing = [mc for mc in model_cols if mc.lower() not in live]
    print(f"[{tabla}] {'FALTAN: ' + ', '.join(missing) if missing else 'OK'} ({len(model_cols)} cols modelo)")

print("\n===== TABLAS DETALLE (presupuestos, SQL crudo) =====")
DETALLE = {
    'cot005':  ['loc_cod','pre_nro','pre_lin','pre_des','pre_de1','pre_de2','pre_de3','pre_de4','pre_cpr','pre_pre','pre_dct'],
    'cot005l': ['loc_cod','pre_nro','pre_lin','pre_dtlin','Pre_DtTip','Pre_DtCant','Pre_DtPre','Pre_DtDescrip'],
}
for tabla, req in DETALLE.items():
    live, err = live_cols(tabla)
    if live is None:
        print(f"[{tabla}] NO EXISTE ({err})"); continue
    missing = [mc for mc in req if mc.lower() not in live]
    print(f"[{tabla}] {'FALTAN: ' + ', '.join(missing) if missing else 'OK'}")

req_loc = ['Loc_cod','Loc_des','loc_est']
live, err = live_cols('loc001')
miss_loc = [x for x in req_loc if x.lower() not in live] if live else None
print(f"\n[loc001] {'NO EXISTE' if live is None else ('FALTAN: ' + ', '.join(miss_loc) if miss_loc else 'OK')}")

s.close(); db.close()
PY
```

**Interpretar:**
- Todo `OK` → el tenant queda **100% operativo** (presupuestos + órdenes).
- `adq004` OK pero faltan columnas en `cot013`/`clientea`/`cot005*` → **órdenes de compra funciona igual**; presupuestos requiere que el cliente complete su BD → documentar (paso 8).
- Variantes reales observadas:
  - **mgamaq:** `cot013` sin `Loc_cod`/`Pre_Neto` (usa `pre_suc`) + 8 más; `clientea` -17; `cot005/cot005l` sin `loc_cod`. (Divergencia grande.)
  - **mgacom:** `cot013` solo -5 (columnas de email); `clientea` -17; resto OK. (Divergencia chica.)

---

## 5. Emitir certificado SSL

Los certs de aprobaciones son **por subdominio** (no wildcard), método **webroot (HTTP-01)**, `key_type ecdsa`, y **cuenta ACME `5239744ebdc2bba3102715566dfb64aa`** (hay 2 cuentas en el VPS; hay que especificarla o certbot falla pidiendo elegir).

### 5.1. Conf HTTP temporal (para servir el challenge)

```bash
cat > /root/docker/nginx-proxy/conf.d/aprobaciones-<slug>.lexastech.cl.conf <<'EOF'
server {
    listen 80;
    server_name aprobaciones-<slug>.lexastech.cl;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$server_name$request_uri;
    }
}
EOF
docker exec nginx_proxy nginx -t && docker exec nginx_proxy nginx -s reload
```
> ⚠️ Reemplazá `<slug>` también dentro del heredoc (el `server_name`).

### 5.2. Emitir el certificado

```bash
docker exec nginx_certbot certbot certonly \
  --webroot -w /var/www/certbot \
  -d aprobaciones-<slug>.lexastech.cl \
  --key-type ecdsa \
  --account 5239744ebdc2bba3102715566dfb64aa \
  --non-interactive --agree-tos
```

Esperar `Successfully received certificate`. (Renovación automática: el contenedor `nginx_certbot` corre `certbot renew` cada 12 h.)

---

## 6. Configurar nginx (conf completa HTTP+HTTPS)

**No pegar el conf completo a mano** (el heredoc largo se corrompe al pegar, y el base64 a mano también). El método confiable es **copiar un conf existente y reemplazar el slug con `sed`**:

```bash
# Copiar un conf que ya funciona (ej. mga) como base
cp /root/docker/nginx-proxy/conf.d/aprobaciones-mga.lexastech.cl.conf \
   /root/docker/nginx-proxy/conf.d/aprobaciones-<slug>.lexastech.cl.conf

# Reemplazar el slug de la plantilla por el nuevo
sed -i 's/mga\b/<slug>/g' /root/docker/nginx-proxy/conf.d/aprobaciones-<slug>.lexastech.cl.conf
# (si copiaste de mgamaq/mgacom, usar: sed -i 's/mgamaq/<slug>/g' ... )

# Confirmar que reemplazó bien (solo <slug>, ningún slug viejo)
grep -E 'server_name|ssl_certificate |access_log' \
  /root/docker/nginx-proxy/conf.d/aprobaciones-<slug>.lexastech.cl.conf

# Validar y recargar
docker exec nginx_proxy nginx -t && docker exec nginx_proxy nginx -s reload
```

> El conf usa `listen 443 ssl;` + `http2 on;` (sintaxis nueva). Warnings benignos al recargar: `listen ... http2 is deprecated` y `protocol options redefined for 0.0.0.0:443` — son normales (los tienen varios dominios) y **no** rompen nada. Lo que importa es `configuration file test is successful`.

---

## 7. Verificación final

```bash
curl -sI https://aprobaciones-<slug>.lexastech.cl   # esperar: HTTP/2 200 (x-powered-by: Next.js)
curl -sI http://aprobaciones-<slug>.lexastech.cl    # esperar: 301 -> https
```

Verificación de tenant vía API (desde cualquier máquina):

```bash
curl -s https://api.lexastech.cl/api/v1/tenant/config \
  -H "X-Tenant-Domain: aprobaciones-<slug>.lexastech.cl"
# Debe devolver slug, nombre, dominio y la paleta del tema.
```

Checklist:
- [ ] `HTTP/2 200` en HTTPS y `301` en HTTP.
- [ ] `/tenant/config` resuelve el tenant (no 404).
- [ ] Paso 3 dio `CONEXION OK`.
- [ ] Paso 4: `adq004` OK (órdenes operativo).
- [ ] Frontend abre en el navegador con el tema del tenant.

> **Frontend:** no requiere cambios (es dinámico por hostname). Si `/tenant/config` resuelve, el front funciona.

---

## 8. Documentar ajustes de BD pendientes (si los hay)

Si el paso 4 mostró columnas faltantes, crear un doc `docs/COMPATIBILIDAD_BD_<SLUG>.md` para el cliente con: tablas/columnas faltantes (nombre, tipo, nulabilidad, significado), DDL `ALTER TABLE` sugerido y cómo re-validar. Usar como plantilla:
- [docs/COMPATIBILIDAD_BD_MGACOM.md](COMPATIBILIDAD_BD_MGACOM.md) — caso divergencia chica (5 cols + clientea).
- [docs/COMPATIBILIDAD_BD_MAQUINARIA.md](COMPATIBILIDAD_BD_MAQUINARIA.md) — caso divergencia grande (incl. `Loc_cod`/`Pre_Neto` y la clave compuesta).

Luego actualizar la tabla de tenants en [AGENTS.md](../AGENTS.md) (URLs por tenant + tabla de BDs).

---

## 9. Lecciones aprendidas / gotchas

| # | Problema | Solución |
| :-: | :--- | :--- |
| 1 | `db_name` (o user/host) con **espacio al final** → MySQL responde `Incorrect database name` y el endpoint da **500**. | El script del paso 3 hace `.strip()` y `commit()`. Siempre correrlo antes que nada. |
| 2 | Cloudflare deja el registro **proxied (naranja)** → resuelve a IPs de CF, no al VPS. | Ponerlo **DNS-only (gris)**. Verificar con `@1.1.1.1` (el caché local engaña). |
| 3 | `certbot` falla con *"Please choose an account"* (hay 2 cuentas ACME). | Pasar `--account 5239744ebdc2bba3102715566dfb64aa`. |
| 4 | Pegar el conf de nginx completo (heredoc largo / base64) se **corrompe**. | `cp` de un conf existente + `sed` del slug. Verificar con `grep`. |
| 5 | `/tenant/db-check` dice OK pero presupuestos falla. | El `db-check` valida solo un subconjunto. Usar el script ORM del paso 4 (autoritativo). |
| 6 | Presupuestos no anda en un tenant pero órdenes sí. | El ERP del cliente tiene schema divergente en `cot013`/`clientea`/`cot005*`. Documentar (paso 8); órdenes funciona igual. |
| 7 | Warnings `http2 deprecated` / `protocol options redefined` al recargar nginx. | Benignos. Mirar que diga `test is successful`. |

---

**📌 Referencias:** [AGENTS.md](../AGENTS.md) · [nginx-proxy/README.md](../nginx-proxy/README.md) · migración [`0002_create_tenant_tables.py`](../alembic/versions/0002_create_tenant_tables.py) · modelos en [`app/models/`](../app/models/)
