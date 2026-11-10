# Backend BranchIt — comandos rápidos

## 1. Instalar dependencias
```
pip install -r requirements.txt
```

## 2. Configurar la base de datos
Copia `.env.example` a `.env` y ajusta `DATABASE_URL` con tus datos de Postgres
(usuario, clave, host, puerto, nombre de la base). Debes crear la base de datos
vacía en Postgres antes (ej: `createdb branchit`).

## 3. Aplicar las migraciones (crea las tablas)
```
alembic upgrade head
```

## 4. Levantar el servidor
```
uvicorn app.main:app --reload
```
Docs interactivas en http://localhost:8000/docs

## Endpoints de hoy (Sprint 3 y parte de Sprint 5)
- POST /auth/registro/egresado
- POST /auth/registro/empresa
- GET/PUT/DELETE /egresados/{usuario_id}
- GET /egresados/{usuario_id}/ofertas  → hub de ofertas para el egresado
- POST/GET/PUT/DELETE /empresas/{usuario_id}/ofertas y /empresas/{usuario_id}/ofertas/{oferta_id}

Nota: como el login todavía no está implementado, estas rutas reciben el
`usuario_id` directamente en la URL. Cuando se implemente el login (siguiente
sprint), se reemplaza por el usuario autenticado vía JWT.
