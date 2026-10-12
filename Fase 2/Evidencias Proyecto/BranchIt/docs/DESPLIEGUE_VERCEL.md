# Despliegue de BranchIT en Vercel y Neon

Estado: publicado y validado en producción el 6 de octubre de 2026.

- Aplicación: https://branchit-blue.vercel.app
- API: https://branchit-api.vercel.app
- Neon: proyecto `BranchIt`, región São Paulo; migración `0004_identidad_empresa` aplicada.
- Rama de producción: `Roberto-branch`.

Validación contra la API pública: registro e inicio de sesión de ambos roles,
presentación del egresado, oferta con pregunta personalizada, postulación,
consulta por la empresa y descifrado correcto de sus respuestas. Se verificaron
rechazo de duplicados (409), restricciones de rol (403), ausencia de sesión (401),
revocación al cerrar sesión y CORS para el frontend. La ruta pública
`/iniciar-sesion` carga directamente desde Vercel.

Se dejaron dos cuentas ficticias y una oferta marcada DEMO para la presentación.
Sus credenciales están únicamente en el archivo local ignorado
`.vercel/demo-credentials.json`; no forman parte del repositorio.

Usar dos proyectos Vercel del repositorio Capstone, rama Roberto-branch:

| Proyecto | Root Directory | Framework |
| --- | --- | --- |
| Frontend | Fase 2/Evidencias Proyecto/BranchIt/frontend | Vite |
| API | Fase 2/Evidencias Proyecto/BranchIt/backend | FastAPI |

El backend exporta `app` desde `app/main.py`. El frontend compila con
`npm run build` a `dist`; `vercel.json` resuelve las rutas de React Router.

En el proyecto frontend, mantener desactivada la opción **Include source files
outside of the Root Directory in the Build Step** (`sourceFilesOutsideRootDirectory: false`).
El frontend no necesita archivos externos a su raíz. Con esta opción activada,
Vercel incorporaba `Fase 2/Evidencias Proyecto/BranchIt/frontend` al nombre de
las funciones `api/media-*.js`, y rechazaba los espacios de esa ruta.
La corrección se aplicó en Vercel y se verificó con un despliegue de producción
en estado READY y respuestas de las tres funciones.
Este ajuste pertenece al proyecto Vercel; no agregar esa propiedad a `vercel.json`.

## Variables

Configurar en el backend, fuera del repositorio:

- `DATABASE_URL`: conexión PostgreSQL de Neon, con TLS según la cadena del proveedor.
- `SECRET_KEY`: clave privada estable para JWT.
- `DATA_ENCRYPTION_KEY`: clave Fernet privada estable para las postulaciones.
- `CORS_ORIGINS`: origen HTTPS exacto del frontend, sin barra final. Separar
  múltiples orígenes con comas.

Configurar en el frontend:

- `VITE_API_URL`: `https://branchit-api.vercel.app`, sin barra final.
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

Se espera `0004_identidad_empresa (head)`. Las migraciones se ejecutan como un paso
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


## Registro y perfil de empresa (12 de octubre de 2026)

La migración `0004_identidad_empresa` agrega RUT único, teléfono y fecha de
identidad a usuarios, y una referencia a foto de empresa. Los registros nuevos
requieren esos datos, además de carrera (egresado) o giro comercial (empresa).
Las cuentas previas conservan valores nulos; no se inventan antecedentes.
RUT, teléfono de registro y fecha no se incluyen en las respuestas públicas.

La empresa edita nombre, resumen y foto en `/perfil-empresa`. Cambiar contraseña
requiere la actual, revoca tokens anteriores y devuelve una sesión nueva.
Las fotos usan la reserva y verificación privada de Vercel Blob; solo se puede
asociar una foto verificada de la misma cuenta. La validación local de permisos
no sustituye una prueba de carga real tras desplegar frontend y backend.

Subir los cambios a `Roberto-branch` para desplegar ambos proyectos. La migración
ya está aplicada en Neon y es compatible con el código anterior.
