# 🌐 Nginx Proxy Centralizado

Proxy reverso centralizado que maneja **todos** los dominios del VPS en los puertos 80 (HTTP) y 443 (HTTPS).

## 📁 Ubicación en VPS

```
/root/docker/nginx-proxy/
├── docker-compose.yml
├── nginx.conf
├── conf.d/
│   ├── api.lexastech.cl.conf
│   └── [otros-dominios].conf
└── certbot/
    ├── conf/     # Certificados SSL
    └── www/      # ACME challenges
```

## 🚀 Servicios

### Nginx
- **Puerto 80**: HTTP (redirige a HTTPS)
- **Puerto 443**: HTTPS con SSL
- **Red**: `general-net` (acceso a todos los contenedores)

### Certbot
- Renovación automática de certificados cada 12 horas
- Certificados válidos por 90 días (Let's Encrypt)

## ➕ Agregar un Nuevo Dominio

### 1. Crear archivo de configuración

Crea `/root/docker/nginx-proxy/conf.d/nuevo-dominio.com.conf`:

```nginx
# Ejemplo: nuevo-dominio.com
server {
    listen 80;
    server_name nuevo-dominio.com www.nuevo-dominio.com;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name nuevo-dominio.com www.nuevo-dominio.com;

    ssl_certificate /etc/letsencrypt/live/nuevo-dominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/nuevo-dominio.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;

    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    client_max_body_size 50M;

    location / {
        # Cambia 'nombre_contenedor' por el nombre del contenedor de tu servicio
        proxy_pass http://nombre_contenedor:puerto;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

### 2. Crear configuración temporal HTTP (para obtener certificado)

Primero crea solo la parte HTTP:

```bash
cd /root/docker/nginx-proxy
cat > conf.d/nuevo-dominio.com.conf << 'EOF'
server {
    listen 80;
    server_name nuevo-dominio.com;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        proxy_pass http://nombre_contenedor:puerto;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF
```

### 3. Recargar Nginx

```bash
docker exec nginx_proxy nginx -s reload
```

### 4. Obtener certificado SSL

```bash
cd /root/docker/nginx-proxy
docker compose exec certbot certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  -d nuevo-dominio.com \
  -d www.nuevo-dominio.com \
  --email tu-email@ejemplo.com \
  --agree-tos \
  --non-interactive
```

**Importante:** Asegúrate de que el DNS del dominio apunte al VPS antes de ejecutar este comando.

### 5. Actualizar configuración con HTTPS

Reemplaza el archivo con la configuración completa (HTTP + HTTPS del paso 1) y recarga:

```bash
docker exec nginx_proxy nginx -s reload
```

### 6. Verificar

```bash
# HTTP (debe redirigir a HTTPS)
curl -I http://nuevo-dominio.com

# HTTPS
curl -I https://nuevo-dominio.com
```

## 🔧 Comandos Útiles

### Ver logs
```bash
docker logs nginx_proxy -f
docker logs nginx_certbot
```

### Ver certificados
```bash
docker compose exec certbot certbot certificates
```

### Renovar certificado manualmente
```bash
docker compose exec certbot certbot renew
docker exec nginx_proxy nginx -s reload
```

### Reiniciar servicios
```bash
cd /root/docker/nginx-proxy
docker compose restart nginx
```

### Ver configuración actual
```bash
docker exec nginx_proxy nginx -T
```

### Verificar sintaxis
```bash
docker exec nginx_proxy nginx -t
```

## 📋 Dominios Activos

| Dominio | Contenedor | Puerto | Estado |
|---------|------------|--------|--------|
| `api.lexastech.cl` | `mcn_backend` | 8000 | ✅ Activo |

## 🔐 Gestión de Certificados

### Ubicación de certificados
```
/root/docker/nginx-proxy/certbot/conf/live/[dominio]/
├── fullchain.pem      # Certificado + cadena
├── privkey.pem        # Clave privada
├── cert.pem           # Solo certificado
└── chain.pem          # Solo cadena
```

### Renovación automática
Certbot verifica automáticamente cada 12 horas si hay certificados por renovar (< 30 días de expiración).

### Forzar renovación
```bash
docker compose exec certbot certbot renew --force-renewal
docker exec nginx_proxy nginx -s reload
```

## 🐛 Troubleshooting

### Error: Port 80 already allocated
Verifica que no haya otro nginx corriendo:
```bash
docker ps | grep nginx
netstat -tulpn | grep :80
```

### Error: Certificate validation failed
1. Verifica que el DNS apunte al VPS
2. Verifica que el puerto 80 sea accesible externamente
3. Revisa logs: `docker logs nginx_certbot`

### Nginx no recarga configuración
```bash
# Verificar sintaxis
docker exec nginx_proxy nginx -t

# Ver logs
docker logs nginx_proxy --tail 50
```

### Certificado no se renueva
```bash
# Ver cuándo expira
docker compose exec certbot certbot certificates

# Verificar logs
docker logs nginx_certbot --tail 100
```

## 🔄 Migrar dominio existente

Si tienes un dominio con certificado en otro nginx:

1. Copia el certificado:
```bash
cp -r /ruta/anterior/letsencrypt/live/dominio.com \
      /root/docker/nginx-proxy/certbot/conf/live/
```

2. Crea la configuración en `conf.d/`
3. Recarga nginx
4. Actualiza el contenedor para conectarse a `general-net`

## 📚 Recursos

- [Nginx Documentation](https://nginx.org/en/docs/)
- [Let's Encrypt](https://letsencrypt.org/)
- [Certbot Documentation](https://eff-certbot.readthedocs.io/)
