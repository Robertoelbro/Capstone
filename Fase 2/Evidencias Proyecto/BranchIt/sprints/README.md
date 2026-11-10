# Avance de sprints · BranchIT

Estado revisado el 9 de noviembre de 2026. Los README antiguos conservan evidencias históricas; sus conteos no representan el resultado actual.

| Sprint | Funciones implementadas | Verificación |
| --- | --- | --- |
| [4](sprint_4/README.md) | Login, permisos por rol y hubs. | Recorridos y pruebas automatizadas. |
| [5](sprint_5/README.md) | Portafolio, ofertas y formularios de empresa. | CRUD, validaciones y privacidad. |
| [6](sprint_6/README.md) | Postulación dinámica, cifrado e historial privado. | Permisos, versiones y cifrado. |
| [7](sprint_7/README.md) | Gemini, entrevista diaria, preparación por oferta y certificaciones. | Proveedor simulado; validar contenido real en producción. |
| [8](sprint_8/README.md) | Contratación desde reclutador, bloqueo de postulaciones, finiquito PDF privado, regla de un año y desactivación. | API, migraciones y navegador con cuentas ficticias. |
| [9](sprint_9/README.md) | Refuerzo de seguridad, límites de solicitudes, errores genéricos, cabeceras y dependencias. | Pruebas adversariales y revisión de dependencias de producción. |
| [10](sprint_10/README.md) | Regresión, carga sintética reproducible y protocolo de piloto/accesibilidad. | Ejecución local; piloto real y carga remota pendientes. |

## Resultado local

- Backend: 75 casos verificados, incluidos seguimiento, contratación/finiquito, seguridad, suscripción y beneficios.
- Migraciones: hasta `0012_entrevistas_suscripcion`; conservación de datos, comparación con modelos, reversión y SQL PostgreSQL comprobados. [Aplicación en Neon](../docs/CONTRATACION_FINIQUITO_2026-11-09.md).
- Frontend: lint y compilación aprobados. Rutas `/seguimiento` y `/cuenta` incorporadas.
- Dependencias de producción npm: cero avisos después de las correcciones. No equivale a ausencia de vulnerabilidades desconocidas ni a auditoría externa.
- Carga: 200 lecturas sintéticas con 100 ofertas, a concurrencia 1 y 10; cero errores. [Métricas y limitaciones](../docs/VALIDACION_SPRINT_10.md).
- Navegador: confirmación requerida, estado guardado, formulario bloqueado al trabajar y cierre de sesión al desactivar. [Capturas ficticias](sprint_8/evidencias/).

## Activación en Vercel y Neon

El despliegue existente se adelantó al sprint 11. Neon BranchIt/main/neondb ya se migró hasta `0012`, con respaldo. Los cambios de código siguen locales: falta publicarlos y desplegarlos.

1. En otras bases, respaldar y ejecutar `alembic upgrade head` desde `backend`, con su conexión privada configurada. Se espera `0012_entrevistas_suscripcion`. No repetir el SQL de migración sobre Neon ya actualizado.
2. Publicar los cambios y desplegar frontend y API. Node debe ser 20 o superior.
3. Comprobar `/health` y `/health/ready`, y probar con cuentas ficticias en un entorno de ensayo.

Los endpoints de salud no muestran conexiones ni credenciales. El segundo devuelve 503 si faltan las tablas/columnas nuevas. Conservar las claves de cifrado existentes. La suscripción cuesta $2.990 CLP/mes y sus beneficios están implementados; Webpay permanece sin cobros hasta terminar la integración transaccional.

## Próxima etapa

Sprint 11: validación y entrega final, incluyendo piloto con usuarios, comprobación del despliegue y cierre de documentación. Los protocolos del sprint 10 están preparados; no se presentan como actividades ya realizadas con personas reales.

## Vista local reproducible

Desde `backend`: `.\.venv\Scripts\python.exe scripts/preview_sprints.py`.

Desde `frontend`:

```powershell
$env:VITE_API_URL='http://127.0.0.1:8001'
$env:VITE_DEMO_MODE='true'
npm run dev -- --host 127.0.0.1 --port 5174 --strictPort
```

El script crea una base SQLite desechable con migraciones y cuentas ficticias. No modifica Neon. Los datos desaparecen al detenerlo. Las cuentas se describen en el script; no deben usarse en producción.
