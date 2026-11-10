# Validación de calidad · Sprint 10

## Ensayo ejecutado

Fecha local: 8 de noviembre de 2026, America/Santiago. Entorno: Windows, Python 3.14.5. Herramienta: `backend/scripts/load_smoke.py`, API ASGI mediante `TestClient`, base SQLite temporal. Los modelos crean el esquema para este ensayo; la validación de la cadena de migraciones corresponde a las pruebas de Alembic, no a este script.

Datos: una empresa, un egresado y cien ofertas ficticias. No son clientes, postulantes ni ofertas de producción. Los JWT y claves se generan solo para el proceso y no se escriben en el informe. La configuración se fija antes de importar la aplicación y se impide la lectura de `.env`.

Las solicitudes alternan entre:

| Ruta | Qué se verifica |
| --- | --- |
| `GET /api/employment/jobs` | HTTP 200 y lista con las 100 ofertas. |
| `GET /auth/me` | HTTP 200 e identidad de la cuenta ficticia autenticada. |
| `GET /egresados/{id}/recomendaciones` | HTTP 200 y 100 recomendaciones calculadas para el perfil ficticio. |

Cada escenario calienta primero las tres rutas. Esas seis solicitudes de calentamiento no se incluyen en las 200 medidas. Cada worker utiliza su propio cliente. Los percentiles usan el método de rango más cercano; los tiempos incluyen el paso por el cliente de prueba y la aplicación en el mismo equipo.

| Workers | Solicitudes medidas | Errores | p50 | p95 | Solicitudes/s |
| --- | --- | --- | --- | --- | --- |
| 1 | 100 | 0 | 13,48 ms | 32,59 ms | 62,99 |
| 10 | 100 | 0 | 184,86 ms | 369,29 ms | 52,26 |

Los 200 estados fueron HTTP 200 y se validó la forma y cantidad esperada de sus datos. El criterio del smoke es cero errores de transporte, servidor o contenido. No se define un SLA de producción a partir de estas mediciones. La mayor concurrencia aumenta la latencia en este ensayo; los resultados dependen del equipo, de SQLite y de la instrumentación de `TestClient`.

El [JSON de esta ejecución](../sprints/sprint_10/evidencias/carga-local.json) se conserva como evidencia, sin credenciales. Las ejecuciones nuevas escriben por defecto `.vercel/sprint10-load-smoke.json`. Puede regenerarse con el comando indicado en el [README del sprint](../sprints/sprint_10/README.md).

## Lo que el ensayo no demuestra

No mide navegador, red, arranques en frío, bloqueos de PostgreSQL, pool de conexiones de Neon, subidas a Blob, consumo de Gemini ni límites de Vercel. Tampoco certifica WCAG, seguridad o inserción laboral. No se efectuó una prueba de carga contra los servicios desplegados.

Antes de medir capacidad remota, preparar una vista previa y una rama de BD separadas, cuentas sintéticas y un presupuesto de solicitudes. Acordar concurrencia, duración, cuotas del plan y un criterio de parada por errores. Evitar la producción y los datos personales. Las llamadas reales a Gemini y la carga de archivos deben tratarse como escenarios separados para no consumir sus cuotas accidentalmente.

## Protocolo de piloto pendiente

Este protocolo está preparado; no se afirma que hayan participado usuarios reales. Solicitar consentimiento, usar datos ficticios, permitir retirarse y guardar resultados anónimos. Registrar tareas completadas, errores, ayudas necesarias y comentarios, sin contraseñas, RUT, contacto personal o contenido privado del portafolio.

| Rol | Tarea | Evidencia por recoger |
| --- | --- | --- |
| Egresado | Registrarse, iniciar sesión y completar el perfil. | Éxito, tiempo observado, campos que causan dudas. |
| Egresado | Añadir un proyecto y publicar/despublicar el portafolio. | Comprensión de la privacidad y acceso público esperado. |
| Egresado | Encontrar una oferta y enviar una postulación. | Comprensión de requisitos, afinidad y confirmación. |
| Empresa | Crear una oferta y agregar una pregunta de selección. | Completitud de los campos y facilidad del editor. |
| Empresa | Revisar antecedentes y abrir el portafolio del postulante. | Localización de experiencia, proyectos y certificaciones. |
| Empresa | Cerrar la convocatoria y guardar su selección privada. | Claridad del cierre y ausencia de ganador en la vista del egresado. |
| Egresado | Confirmar contratación y comprobar el bloqueo de nuevas postulaciones. | Mensaje claro y conservación del historial/portafolio. |
| Ambos | Desactivar una cuenta ficticia desde Cuenta y seguridad. | Comprensión de efectos y sesión invalidada. |

Repetir las tareas críticas con participantes de ambos roles. Definir el tamaño del piloto con el equipo y el docente, sin inventar una muestra ya realizada. Clasificar las incidencias por impacto: bloqueo del recorrido, privacidad/permisos, confusión de uso o detalle visual. Corregir y repetir las tareas afectadas antes del cierre.

## Revisión manual de accesibilidad pendiente

- Navegar sin mouse: orden de foco, acceso a menús y formularios, cierre de diálogos y retorno del foco.
- Comprobar nombres accesibles de los controles, etiquetas, mensajes de error asociados y avisos de guardado con lector de pantalla.
- Revisar contraste de texto, estados y foco; no comunicar errores ni selección exclusivamente con color.
- Probar aumento de texto/zoom, ancho de 320 px, contenido extenso y desplazamiento de paneles sin ocultar botones.
- Verificar formularios vacíos, valores inválidos, doble envío, sesión vencida y fallo de conexión, conservando el texto recuperable.
- Comprobar uso del asistente IA con teclado y explicación del límite diario. Para evaluar el contenido de Gemini se requiere una ejecución específica con datos ficticios y cuota disponible.

Registrar navegador, ancho o zoom, tarea, resultado, incidencia y captura de ejemplo con datos ficticios. Una prueba automatizada o una revisión parcial no reemplaza estas evidencias ni equivale a una certificación.

## Registro de ejecución por completar

| Actividad | Estado al preparar esta evidencia |
| --- | --- |
| Smoke local sintético de lectura, 1 y 10 workers | Ejecutado: resultados arriba. |
| Piloto con egresados y reclutadores reales | Pendiente de participantes y ejecución. |
| Revisión manual completa de teclado, lector y zoom | Pendiente de ejecución documentada. |
| Carga remota en entorno de ensayo con PostgreSQL | Pendiente; no se atacó producción. |
| Evaluación de respuestas reales del proveedor de IA | Pendiente de escenario y cuota. |
| Auditoría externa de seguridad | No realizada; no se presenta la revisión interna como auditoría certificada. |
