# Sprint 9 · Revisión interna de seguridad

## Cambios aplicados

- Límite de 512 KiB por solicitud antes de interpretar JSON. Cuenta también los bytes recibidos por fragmentos, sin confiar en el tamaño declarado. Los binarios se suben a Blob, no a esta API.
- Cabeceras `no-store`, `nosniff`, `no-referrer` y protección contra marcos, también en rechazos por tamaño y errores inesperados.
- Excepciones SQLAlchemy y errores no controlados con mensajes genéricos, sin SQL, parámetros, conexiones ni claves. Las validaciones siguen omitiendo los valores de entrada sensibles.
- CORS normaliza los orígenes configurados y rechaza orígenes ajenos.
- Las mutaciones de recursos bloquean primero la fila del titular y revalidan actividad y versión de sesión, para no continuar detrás de una desactivación o revocación concurrente.
- La IA no usa como contexto ofertas de empresas desactivadas.
- Vercel: cabeceras contra MIME sniffing, marcos, envío del referente y permisos innecesarios. CSP básica para `base-uri`, `object-src`, `frame-ancestors` y `form-action`; no se declara una política completa de aislamiento de scripts.
- El fallback de la SPA excluye `/_vercel/` además de `/api/`, preservando Analytics.
- `/health` comprueba API; `/health/ready` comprueba acceso a la tabla de `0009`, sin exponer infraestructura.

## Dependencias

La consulta inicial de producción detectó 6 avisos altos y 2 moderados, incluidos transitivos. Se actualizaron `undici` y `cross-spawn` y se añadió un override de Zod 4.6.6 o superior para `@vercel/cli-config`. No se degradó Blob, porque la alternativa sugerida por audit eliminaría APIs usadas para archivos privados.

React Router pasó de la rama 6 a la 7 corregida, conservando modo declarativo e importaciones `react-router-dom`. Requiere React 18 y Node 20 o superior. Se verificaron rutas, sesión, navegación, lint y build.

Resultado posterior: **0 avisos de producción** en `npm audit --omit=dev`. Es una consulta en la fecha de ejecución; no garantiza el código propio, Python, dependencias de desarrollo o vulnerabilidades desconocidas. No se contrataron servicios.

## Pruebas

Nueve pruebas en `backend/tests/test_security_hardening.py`: límite declarado y por fragmentos, tamaños ambiguos, solicitudes válidas, salud/esquema, fallos SQL y no controlados sin secretos, validación/autenticación y CORS. Con las ampliaciones de contratación y suscripción se verificaron 75 casos; también cubren JWT, permisos, archivos privados, formularios, cifrado y revocación.

## Límites de producción

El limitador de autenticación existente es por proceso: no ofrece cuota distribuida entre instancias de Vercel. Antes de uso público amplio, añadir protección compartida o de plataforma. Los endpoints históricos de eliminación conservan su comportamiento; la nueva interfaz usa desactivación con contraseña. La revisión interna no es una auditoría independiente ni una certificación WCAG.

Referencias consultadas: [middleware FastAPI](https://fastapi.tiangolo.com/advanced/middleware/), [cabeceras Vercel](https://vercel.com/docs/headers), [cambios y requisitos de React Router](https://reactrouter.com/changelog).
