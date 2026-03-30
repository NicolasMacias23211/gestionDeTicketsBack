# Sistema de Gestión de Tickets E-SEUS — Backend API

API REST desarrollada con Django 5 + Django REST Framework para el sistema de gestión de tickets del área de E-learning.

---

## Tabla de Contenidos

- [Requisitos Previos](#requisitos-previos)
- [Variables de Entorno](#variables-de-entorno)
- [Inicio Rápido (Desarrollo)](#inicio-rápido-desarrollo)
- [Despliegue en Producción (Linux)](#despliegue-en-producción-linux)
  - [1. Preparar el Servidor](#1-preparar-el-servidor)
  - [2. Clonar el Proyecto](#2-clonar-el-proyecto)
  - [3. Configurar Variables de Entorno](#3-configurar-variables-de-entorno)
  - [4. Instalar Dependencias](#4-instalar-dependencias)
  - [5. Configurar la Base de Datos MySQL](#5-configurar-la-base-de-datos-mysql)
  - [6. Ejecutar Migraciones y Collectstatic](#6-ejecutar-migraciones-y-collectstatic)
  - [7. Configurar Gunicorn como Servicio](#7-configurar-gunicorn-como-servicio)
  - [8. Configurar Nginx como Reverse Proxy](#8-configurar-nginx-como-reverse-proxy)
  - [9. Verificar el Despliegue](#9-verificar-el-despliegue)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Comandos Útiles](#comandos-útiles)
- [Solución de Problemas](#solución-de-problemas)

---

## Requisitos Previos

| Componente     | Versión requerida | Notas                          |
|----------------|-------------------|--------------------------------|
| Python         | 3.11+             |                                |
| MySQL          | 8.0+              |                                |
| Nginx          | 1.18+             | Solo producción (reverse proxy)|
| Git            | 2.x               |                                |

---

## Variables de Entorno

Todas las variables se leen desde un archivo `.env` en la raíz del proyecto usando `python-decouple`.

> **Copia `.env.example` como `.env` y ajusta los valores.**

### Variables Obligatorias

| Variable             | Descripción                                   | Ejemplo Producción                        |
|----------------------|-----------------------------------------------|-------------------------------------------|
| `SECRET_KEY`         | Clave secreta de Django (única y aleatoria)   | `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `DEBUG`              | Modo debug (**siempre `False` en producción**)| `False`                                   |
| `ALLOWED_HOSTS`      | Dominios/IPs permitidos (separados por comas) | `e-seus.emtelco.com.co,10.0.0.50`        |
| `DJANGO_SETTINGS_MODULE` | Módulo de configuración Django            | `config.settings.production`              |
| `DB_NAME`            | Nombre de la base de datos MySQL              | `e-seus`                                  |
| `DB_USER`            | Usuario MySQL                                 | `eseus_user`                              |
| `DB_PASSWORD`        | Contraseña MySQL                              | `(contraseña segura)`                     |
| `DB_HOST`            | Host del servidor MySQL                       | `localhost` o IP/endpoint                 |
| `DB_PORT`            | Puerto MySQL                                  | `3306`                                    |

### Variables Opcionales (con defaults)

| Variable               | Default                          | Descripción                              |
|------------------------|----------------------------------|------------------------------------------|
| `CORS_ALLOWED_ORIGINS` | `http://localhost:3000,...`       | Orígenes CORS permitidos (producción: URL del frontend) |
| `DJANGO_LOG_LEVEL`     | `INFO`                           | Nivel de logging (`WARNING` recomendado en prod) |
| `EMAIL_HOST`           | `smtp.gmail.com`                 | Servidor SMTP                            |
| `EMAIL_PORT`           | `587`                            | Puerto SMTP                              |
| `EMAIL_USE_TLS`        | `True`                           | Usar TLS para email                      |
| `EMAIL_HOST_USER`      | (vacío)                          | Usuario SMTP                             |
| `EMAIL_HOST_PASSWORD`  | (vacío)                          | Contraseña SMTP                          |
| `DEFAULT_FROM_EMAIL`   | `noreply@e-seus.com`            | Email de remitente por defecto           |
| `SECURE_SSL_REDIRECT`  | `False`                          | Redirección HTTPS por Django (ver nota SSL) |

> **Nota SSL:** Si nginx ya maneja la redirección HTTP→HTTPS, deja `SECURE_SSL_REDIRECT=False` para evitar redirect loops. Django ya lee el header `X-Forwarded-Proto` de nginx.

---

## Inicio Rápido (Desarrollo)

En **Windows** con PowerShell:

```powershell
# Ejecuta el script automatizado (crea venv, instala deps, migra y levanta el servidor)
.\start.ps1
```

O manualmente:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
cp .env.example .env          # Editar con valores de desarrollo
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

La API estará disponible en:
- http://127.0.0.1:8000/api/docs/ — Documentación API (ReDoc)
- http://127.0.0.1:8000/admin/ — Panel de administración

---

## Despliegue en Producción (Linux)

### 1. Preparar el Servidor

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3.11 python3.11-venv python3.11-dev \
    mysql-server nginx git \
    build-essential libmysqlclient-dev pkg-config -y
```

### 2. Clonar el Proyecto

```bash
# Crear directorio de la aplicación
sudo mkdir -p /var/www/html/e-learning/e-seus/backend
sudo chown $USER:$USER /var/www/html/e-learning/e-seus/backend
cd /var/www/html/e-learning/e-seus/backend

# Clonar repositorio
git clone <URL_DEL_REPOSITORIO> .
```

### 3. Configurar Variables de Entorno

```bash
cp .env.example .env
nano .env
```

**Contenido mínimo del `.env` para producción:**

```env
# ---- OBLIGATORIO: Generar una clave nueva ----
SECRET_KEY=<tu-clave-secreta-generada>

# ---- OBLIGATORIO ----
DEBUG=False
ALLOWED_HOSTS=e-seus.emtelco.com.co,<IP_DEL_SERVIDOR>
DJANGO_SETTINGS_MODULE=config.settings.production

# ---- BASE DE DATOS ----
DB_NAME=e-seus
DB_USER=eseus_user
DB_PASSWORD=<contraseña-segura>
DB_HOST=localhost
DB_PORT=3306

# ---- CORS (URL del frontend) ----
CORS_ALLOWED_ORIGINS=https://e-seus.emtelco.com.co

# ---- LOGGING ----
DJANGO_LOG_LEVEL=WARNING
```

Generar `SECRET_KEY`:

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 4. Instalar Dependencias

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

> **Nota:** En Linux puedes reemplazar `PyMySQL` por `mysqlclient` para mejor rendimiento. Si lo haces, comenta `PyMySQL==1.1.0` y descomenta `mysqlclient==2.2.4` en `requirements.txt`, y comenta el contenido de `config/__init__.py`.

### 5. Configurar la Base de Datos MySQL

```bash
sudo mysql -u root
```

```sql
-- Crear base de datos
CREATE DATABASE IF NOT EXISTS `e-seus` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Crear usuario de producción (Example)
CREATE USER 'eseus_user'@'localhost' IDENTIFIED BY '<contraseña-segura>';
GRANT ALL PRIVILEGES ON `e-seus`.* TO 'eseus_user'@'localhost';
FLUSH PRIVILEGES;

EXIT;
```

Si la base de datos ya tiene tablas legacy, ejecutar los scripts SQL de inicialización:

```bash
sudo mysql -u eseus_user -p e-seus < config/sql/createDatabase.sql
sudo mysql -u eseus_user -p e-seus < config/sql/alter_autoincrement.sql
```

### 6. Ejecutar Migraciones y Collectstatic

```bash
source venv/bin/activate

# Aplicar migraciones
python manage.py migrate --settings=config.settings.production

# Recopilar archivos estáticos
python manage.py collectstatic --noinput --settings=config.settings.production

# (Opcional) Crear superusuario para el panel admin
python manage.py createsuperuser --settings=config.settings.production
```

> **Nota:** `manage.py` usa `config.settings.development` por defecto, por eso hay que pasar `--settings=config.settings.production` explícitamente, o configurar la variable `DJANGO_SETTINGS_MODULE=config.settings.production` en el `.env`.


> **Importante:** `config/wsgi.py` ya tiene `DJANGO_SETTINGS_MODULE=config.settings.production` como default. Si necesitas sobreescribirlo, puedes definirlo en `EnvironmentFile` o como `Environment=` en el servicio.


### 7. Verificar el Despliegue

```bash
# 1. Verificar que el servicio esté corriendo
sudo systemctl status e-seus

# 2. Revisar logs de Gunicorn si hay errores
sudo tail -f /var/www/html/e-learning/e-seus/backend/logs/gunicorn-error.log

# 3. Revisar logs de Django
sudo tail -f /var/www/html/e-learning/e-seus/backend/logs/django.log

# 4. Probar la API desde el servidor
curl -I http://localhost/api/docs/

# 5. Verificar que la conexión a MySQL funciona
source venv/bin/activate
python manage.py check --settings=config.settings.production

# 6. Verificar la configuración de deploy
python manage.py check --deploy --settings=config.settings.production
```

---

## Estructura del Proyecto

```
├── manage.py                  # CLI Django (usa development por defecto)
├── requirements.txt           # Dependencias Python
├── .env.example               # Plantilla de variables de entorno
├── start.ps1                  # Script de inicio rápido (Windows/desarrollo)
├── config/
│   ├── __init__.py            # Configura PyMySQL como driver MySQL
│   ├── wsgi.py                # Punto de entrada WSGI (usa production por defecto)
│   ├── asgi.py                # Punto de entrada ASGI (usa production por defecto)
│   ├── urls.py                # URLs raíz del proyecto
│   ├── settings/
│   │   ├── base.py            # Configuración compartida (todas las variables de entorno)
│   │   ├── development.py     # Overrides para desarrollo (DEBUG=True, CORS abierto)
│   │   └── production.py      # Overrides para producción (seguridad, WhiteNoise)
│   └── sql/                   # Scripts SQL de inicialización
├── apps/
│   ├── authentication/        # Login, JWT tokens
│   ├── tickets/               # CRUD de tickets (modelos, vistas, filtros)
│   └── files/                 # Gestión de archivos adjuntos
├── core/
│   ├── base/                  # Mixins base
│   ├── exceptions/            # Handler de excepciones personalizado
│   ├── middleware/             # Middleware personalizado
│   └── utils/                 # Paginación, validadores, helpers
├── tests/                     # Tests unitarios (pytest)
├── templates/                 # Templates (ReDoc)
├── static/                    # Archivos estáticos (desarrollo)
├── uploads/                   # Archivos subidos
└── logs/                      # Logs de la aplicación
```

### Flujo de Settings

| Punto de entrada  | Settings por defecto                  | Uso                |
|-------------------|---------------------------------------|--------------------|
| `manage.py`       | `config.settings.development`         | CLI, desarrollo    |
| `config/wsgi.py`  | `config.settings.production`          | Gunicorn (producción) |
| `config/asgi.py`  | `config.settings.production`          | ASGI (producción)  |
| `pytest.ini`      | `config.settings.development`         | Testing            |

> Puedes sobreescribir el módulo de settings con la variable de entorno `DJANGO_SETTINGS_MODULE` o con el flag `--settings=...`.

---

## Comandos Útiles

```bash
# Activar entorno virtual
source venv/bin/activate

# Ejecutar migraciones en producción
python manage.py migrate --settings=config.settings.production

# Recopilar estáticos
python manage.py collectstatic --noinput --settings=config.settings.production

# Crear superusuario
python manage.py createsuperuser --settings=config.settings.production

# Verificar configuración de producción
python manage.py check --deploy --settings=config.settings.production

# Reiniciar servicio después de cambios en el código
sudo systemctl restart e-seus

# Ver logs en tiempo real
sudo journalctl -u e-seus -f

# Ejecutar tests
pytest
```

---

## Solución de Problemas

### `set_urlconf(settings.ROOT_URLCONF)` — AttributeError

**Causa:** `DJANGO_SETTINGS_MODULE` apunta a un módulo que no define settings (ej: `config.settings` en lugar de `config.settings.production`).

**Solución:** Verificar que el `.env` tenga `DJANGO_SETTINGS_MODULE=config.settings.production` y que `wsgi.py` apunte al módulo correcto.

### Redirect Loop (ERR_TOO_MANY_REDIRECTS)

**Causa:** `SECURE_SSL_REDIRECT=True` en Django + nginx también redirigiendo a HTTPS.

**Solución:** Dejar `SECURE_SSL_REDIRECT=False` en `.env` y manejar la redirección HTTPS en nginx.

### `ModuleNotFoundError: No module named 'pymysql'` o `mysqlclient`

**Causa:** El entorno virtual no tiene las dependencias instaladas, o Gunicorn usa un Python diferente.

**Solución:** Asegurar que el `ExecStart` de systemd apunte al `gunicorn` dentro del venv:
```
/var/www/.../venv/bin/gunicorn
```

### `DisallowedHost` — Invalid HTTP_HOST header

**Causa:** El dominio/IP usado no está en `ALLOWED_HOSTS`.

**Solución:** Agregar el dominio o IP al `.env`:
```
ALLOWED_HOSTS=e-seus.emtelco.com.co,10.0.0.50
```

### Archivos estáticos no cargan (404)

**Causa:** No se ejecutó `collectstatic` o nginx no apunta al directorio correcto.

**Solución:**
```bash
python manage.py collectstatic --noinput --settings=config.settings.production
# Verificar que /staticfiles/ existe y tiene archivos
ls -la staticfiles/
```

### Permiso denegado en socket o logs

**Causa:** El usuario del servicio (`www-data`) no tiene permisos.

**Solución:**
```bash
sudo chown -R www-data:www-data /var/www/html/e-learning/e-seus/backend
```


