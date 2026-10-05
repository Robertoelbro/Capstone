# Despliegue de BranchIT en Vercel y Neon

Estado: configuración local preparada; publicación y validación remota pendientes.

Usar dos proyectos Vercel del repositorio Capstone, rama Roberto-branch:

| Proyecto | Root Directory | Framework |
| --- | --- | --- |
| Frontend | Fase 2/Evidencias Proyecto/BranchIt/frontend | Vite |
| API | Fase 2/Evidencias Proyecto/BranchIt/backend | FastAPI |

El backend exporta `app` desde `app/main.py`. El frontend compila con
`npm run build` a `dist`; `vercel.json` resuelve las rutas de React Router.

## Variables

Configurar en el backend, fuera del repositorio:

- `DATABASE_URL`: conexión PostgreSQL de Neon, con TLS según la cadena del proveedor.
- `SECRET_KEY`: clave privada estable para JWT.
- `DATA_ENCRYPTION_KEY`: clave Fernet privada estable para las postulaciones.
- `CORS_ORIGINS`: origen HTTPS exacto del frontend, sin barra final. Separar
  múltiples orígenes con comas.

Configurar en el frontend:

- `VITE_API_URL`: URL HTTPS del backend, sin barra final.
- `VITE_DEMO_MODE`: `false`.

Las variables VITE son públicas. No guardar claves ni DATABASE_URL en ellas.
Las variables de Vite se incorporan al compilar: desplegar de nuevo tras cambiarlas.
Conservar DATA_ENCRYPTION_KEY mientras existan postulaciones cifradas.

## Base y validación

Antes de habilitar la aplicación, ejecutar desde backend y con DATABASE_URL
apuntando a la base de destino autorizada:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m alembic current
```

Se espera `0002_postulaciones (head)`. Las migraciones se ejecutan como un paso
controlado, no durante cada solicitud ni automáticamente en cada preview.
No usar el script SQLite temporal en Vercel.

Validar en el despliegue: registro de ambos roles, login, presentación,
creación de oferta, envío y consulta privada de postulación; recargar una
ruta interna y comprobar persistencia. Abrir `/docs` no prueba acceso a la base.

El limitador de autenticación actual usa memoria por proceso; no ofrece un
límite global entre instancias de Vercel. Antes de uso público amplio, añadir
un contador compartido o protección equivalente en la plataforma.

Referencias: https://vercel.com/docs/frameworks/backend/fastapi y
https://vercel.com/docs/frameworks/frontend/vite.
