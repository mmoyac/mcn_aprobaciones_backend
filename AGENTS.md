# 🤖 AGENTS.md: Backend MCN APROBACIONES - Guía Operacional (FastAPI, SQLAlchemy, PostgreSQL)

Este archivo sirve como el **manual de operaciones** y contexto esencial para cualquier agente de codificación o desarrollador 

El objetivo es mantener la consistencia en el entorno, el código y la arquitectura de la base de datos.

---

## 1. ⚙️ Arquitectura del Proyecto y Convenciones

### 1.1. Stack Tecnológico

| Componente | Tecnología | Rol |
| :--- | :--- | :--- |
| **Framework** | FastAPI (Python) | Capa de API REST. |
| **ORM** | SQLAlchemy (Core + ORM) | Mapeo objeto-relacional. |
| **Base de Datos** | PostgreSQL (v14+) | Almacenamiento persistente. |
| **Orquestación** | Docker Compose | Entorno de desarrollo aislado. |
| **Tests** | pytest + httpx | Suite de tests automatizados. |

### 1.2. Estructura del Directorio

El código fuente del backend (`mcn-aprobaciones-backend`) utiliza una arquitectura modular.

### 1.3. Convenciones de Codificación

* **Estilo:** PEP 8 (gestionado por herramientas de *linting* como Black o Ruff).
* **Nomenclatura:** Clases y *routers* en PascalCase. Funciones y variables en snake_case.
* **Gestión de Dependencias:** Se usa **`pip`** y el entorno virtual (`.venv`). El archivo **`requirements.txt`** es la única fuente de verdad para dependencias.

---

## 💾 Base de Datos

* **Servidor:** `179.27.210.204`
* **Base de Datos:** Se usara una bd existente y con tablas ya creadas, en MySql, cosiderar todo lo referente a las versiones 5.7.7 a la 5.7.23

## 2. 🐳 Configuración del Entorno de Desarrollo

Se requiere **Docker** y **Docker Compose** para iniciar el servicio de **`backend`** (FastAPI).

### 2.1. Variables de Entorno (`.env`)

El archivo **`.env`** en la raíz del proyecto es la fuente de configuración. El servicio **`backend`** lo utiliza para definir su conexión a la base de datos.

```bash
# Variables de PostgreSQL (Servicio 'db')
DB_USER=lexasdulce
DB_PASSWORD=Lexas1234
DB_NAME=lexascl_mga

## 📁 Ubicación del DDL

Existe una carpeta **`schema/`** en la raíz 

Para el acceso y desarrollo, la definicion de las tablas esta en `schema/db_tables.sql`
