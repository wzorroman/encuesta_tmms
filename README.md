# Encuesta TMMS-24

Aplicación web para la encuesta TMMS-24 de inteligencia emocional.

## Requisitos

- Python 3.10+
- PostgreSQL

## Instalación

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Base de datos

1. Crear la base de datos `encuesta_tmms` en PostgreSQL.
2. Ejecutar `init_db.sql` para crear las tablas:

```bash
psql -U postgres -d encuesta_tmms -f init_db.sql
```

Variables de entorno para la conexión (opcional, valores por defecto):

| Variable   | Default      |
|------------|-------------|
| DB_HOST    | localhost   |
| DB_PORT    | 5432        |
| DB_NAME    | encuesta_tmms |
| DB_USER    | postgres    |
| DB_PASS    | postgres    |

## Ejecución

```bash
python app.py
```

La app corre en `http://localhost:5000`.

## Panel de administración

URL: `/admin`

### Credenciales por defecto

- **Usuario:** administrador
- **Contraseña:** año2026

Al iniciar la app, si el usuario `administrador` no existe en la BD, se crea automáticamente con la contraseña `año2026`.

### Exportar respuestas

Dentro del panel hay un botón **"Exportar CSV"** que descarga todas las respuestas. Cada fila es un encuestado y cada columna (`P1` a `P24`) es su respuesta a cada pregunta.

### Resetear contraseña

Si se pierde la contraseña:

1. Conectarse a la base de datos.
2. Ejecutar: `DELETE FROM usuarios WHERE username = 'administrador';`
3. Reiniciar la aplicación. Al iniciar, se creará nuevamente el usuario con la contraseña por defecto `año2026`.

## Docker Compose

Levantar el proyecto (PostgreSQL + Web):

```bash
docker compose up -d --build
```

La app corre en `http://localhost:5000`.

| Servicio | Puerto host | Puerto contenedor |
|---|---|---|
| Web (Flask) | `5000` | `5000` |
| PostgreSQL | `5432` | `5432` |

Variables de entorno configuradas automáticamente en `docker-compose.yml`:

| Variable   | Valor            |
|------------|------------------|
| DB_HOST    | db               |
| DB_PORT    | 5432             |
| DB_NAME    | encuesta_tmms    |
| DB_USER    | postgres         |
| DB_PASS    | postgres         |

Detener los contenedores:

```bash
docker compose down
```

Para eliminar también los datos de la BD:

```bash
docker compose down -v
```

# -- Clear cache python --
  $ find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
    
