# 🌐 Configuración de Nginx para MCN Backend

Esta guía explica cómo configurar Nginx como reverse proxy con SSL para tu backend.

---

## 📋 Requisitos Previos

- ✅ Backend desplegado en el VPS con docker-compose
- ✅ Contenedor en la red `general-net`
- ✅ Nginx corriendo en el VPS (ya lo tienes según tu configuración)
- ✅ Dominio apuntando a tu VPS (ejemplo: `api.tudominio.com`)

---

## 🔧 Paso 1: Copiar Configuración de Nginx

### Opción A: Copiar archivo manualmente al VPS

```bash
# En tu VPS, crear el archivo de configuración
nano /root/docker/nginx/conf.d/mcn-backend.conf
```

Copia el contenido del archivo `nginx/mcn-backend.conf` del repositorio.

### Opción B: Usar SCP desde tu máquina local

```powershell
# En PowerShell local
scp nginx/mcn-backend.conf root@168.231.96.205:/root/docker/nginx/conf.d/
```

---

## 📝 Paso 2: Personalizar la Configuración

Edita el archivo y reemplaza:

```bash
# En el VPS
nano /root/docker/nginx/conf.d/mcn-backend.conf
```

**Cambiar:**
- `api.tudominio.com` → Tu dominio real (ejemplo: `aprobaciones.lexastech.com`)
- Verificar rutas de certificados SSL

---

## 🔐 Paso 3: Obtener Certificado SSL con Certbot

Si aún no tienes certificado para tu dominio:

```bash
# En el VPS, detener Nginx temporalmente
docker exec nginx_container_name nginx -s stop

# O si Nginx está como servicio del sistema
systemctl stop nginx

# Obtener certificado
certbot certonly --standalone -d api.tudominio.com

# Reiniciar Nginx
docker exec nginx_container_name nginx -s reload
# O
systemctl start nginx
```

### Si usas Nginx en Docker (como tu ejemplo):

El certbot ya está configurado en tu docker-compose. Solo necesitas:

```bash
# Primera vez - obtener certificado
docker-compose run --rm certbot certonly --webroot \
  --webroot-path=/var/www/certbot \
  -d api.tudominio.com \
  --email tu@email.com \
  --agree-tos \
  --no-eff-email

# Recargar Nginx
docker exec masas_estacion_nginx nginx -s reload
```

---

## ✅ Paso 4: Verificar Configuración

```bash
# Verificar sintaxis de Nginx
docker exec masas_estacion_nginx nginx -t

# Si todo está bien, recargar
docker exec masas_estacion_nginx nginx -s reload
```

---

## 🧪 Paso 5: Probar el Backend

### Desde HTTP (debe redirigir a HTTPS):
```bash
curl -I http://api.tudominio.com/health
```

### Desde HTTPS:
```bash
curl https://api.tudominio.com/health
```

### Documentación:
- **Swagger UI:** https://api.tudominio.com/docs
- **ReDoc:** https://api.tudominio.com/redoc

---

## 🔄 Configuración Alternativa: Sin Docker (Nginx del sistema)

Si tu Nginx NO está en Docker:

```bash
# Copiar configuración
sudo cp nginx/mcn-backend.conf /etc/nginx/sites-available/mcn-backend
sudo ln -s /etc/nginx/sites-available/mcn-backend /etc/nginx/sites-enabled/

# Verificar configuración
sudo nginx -t

# Recargar Nginx
sudo systemctl reload nginx

# Obtener certificado SSL
sudo certbot --nginx -d api.tudominio.com
```

---

## 🌐 Configuración DNS

Asegúrate de que tu dominio apunte a tu VPS:

```
Tipo: A
Nombre: api (o aprobaciones)
Valor: 168.231.96.205
TTL: 3600
```

---

## 🔍 Verificar que el Backend está en la red correcta

```bash
# Verificar que mcn_backend está en general-net
docker network inspect general-net

# Deberías ver "mcn_backend" en la lista de contenedores
```

---

## 🐛 Troubleshooting

### Error: "502 Bad Gateway"

**Causa:** Nginx no puede conectarse al backend

**Solución:**
```bash
# Verificar que el backend está corriendo
docker ps | grep mcn_backend

# Verificar que está en general-net
docker inspect mcn_backend | grep general-net

# Verificar logs del backend
docker logs mcn_backend

# Verificar logs de Nginx
docker logs masas_estacion_nginx
```

### Error: "SSL certificate problem"

**Causa:** Certificado no configurado correctamente

**Solución:**
```bash
# Verificar que los certificados existen
ls -la /etc/letsencrypt/live/api.tudominio.com/

# Renovar certificado si expiró
docker-compose run --rm certbot renew
```

### Backend no responde en general-net

**Causa:** El contenedor no está en la red

**Solución:**
```bash
cd /root/docker/mcn

# Recrear el contenedor
docker-compose down
docker-compose up -d

# Verificar la red
docker network inspect general-net
```

### Puerto 443 ya en uso

**Causa:** Otro servicio usa el puerto

**Solución:**
```bash
# Ver qué usa el puerto 443
netstat -tulpn | grep :443

# Si es otro Nginx, usa el mismo para todos los servicios
# Agrega mcn-backend.conf a tu configuración existente
```

---

## 📊 Monitoreo

### Ver logs en tiempo real:

```bash
# Logs de Nginx
docker logs -f masas_estacion_nginx

# Logs del backend
docker logs -f mcn_backend

# Logs de acceso de Nginx
tail -f /var/log/nginx/mcn_backend_access.log

# Logs de errores de Nginx
tail -f /var/log/nginx/mcn_backend_error.log
```

---

## 🔒 Seguridad Adicional

### Proteger /docs con autenticación básica:

```bash
# Crear archivo de contraseñas
sudo apt install apache2-utils
htpasswd -c /root/docker/nginx/.htpasswd admin

# Agregar a mcn-backend.conf:
location /docs {
    auth_basic "API Documentation";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://mcn_backend:8000/docs;
    ...
}
```

### Limitar acceso por IP:

```nginx
location /docs {
    allow 192.168.1.0/24;  # Tu red
    deny all;
    proxy_pass http://mcn_backend:8000/docs;
    ...
}
```

---

## ✅ Checklist de Configuración

- [ ] Backend desplegado y corriendo en `general-net`
- [ ] Dominio apuntando a la IP del VPS (168.231.96.205)
- [ ] Archivo `mcn-backend.conf` copiado y personalizado
- [ ] Certificado SSL obtenido con Certbot
- [ ] Nginx recargado sin errores
- [ ] `https://api.tudominio.com/health` responde correctamente
- [ ] `https://api.tudominio.com/docs` muestra la documentación

---

**🎉 ¡Backend con HTTPS configurado exitosamente!**
