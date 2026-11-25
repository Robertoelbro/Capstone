# Incidencia de rendimiento observada en QA

## Ensayo HTTP original

El 16 de noviembre de 2026 se ejecutó una prueba acotada de lectura contra una vista previa de Vercel conectada al PostgreSQL aislado de QA, con 100 ofertas ficticias. El runner verificó el marcador de aislamiento antes de enviar el JWT del egresado. No incluyó Gemini, Blob, pagos ni datos de producción.

| Concurrencia | Intentos registrados | Errores | p50 | p95 | Resultado |
| --- | --- | --- | --- | --- | --- |
| 1 | 100 de 100 | 0 | 187,41 ms | 413,16 ms | Completo |
| 5 | 36 de 100 | 2 de transporte | 235,63 ms | 9.823,78 ms | Detenido al detectar errores |

El límite del cliente era 10 segundos y el ritmo máximo configurado, 10 solicitudes por segundo. El segundo escenario quedó incompleto; no equivale a una prueba de capacidad aprobada con cinco usuarios. Sus dos errores fueron peticiones a la lista de ofertas, pero también aumentaron las colas de latencia en sesión y recomendaciones: p95 de 7.295,19 ms y 6.033,41 ms, respectivamente. No hubo respuestas HTTP de error registradas: los fallos fueron clasificados por el cliente como `transport_error`.

El informe agregado original se conserva sin alterar en `.vercel/qa-remote-load-20261116.json`. No contiene tokens ni el origen privado en claro.

## Hallazgo de código confirmado

Los tres listados de ofertas hacían un `JOIN` con la empresa, pero al serializar accedían a `oferta.empresa` sin haber cargado esa relación. SQLAlchemy emitía una consulta adicional por empresa distinta. Con 100 ofertas y diez empresas, la medición local aislada dio:

| Ruta | SELECT antes | SELECT después |
| --- | --- | --- |
| Lista pública de ofertas | 11 | 1 |
| Recomendaciones del egresado | 13 | 3 |
| Lista de ofertas del egresado | 13 | 3 |
| Sesión `/auth/me` | 1 | 1, sin cambios |

Se reutilizó el `JOIN` existente mediante `contains_eager`, manteniendo filtros de actividad, orden, nombre, foto y logo de empresa, y las reglas de afinidad. La prueba `backend/tests/test_job_query_budget.py` comprueba que el número de consultas se mantiene constante al pasar de una a diez empresas y valida el contenido de las cien ofertas, excluyendo una empresa inactiva.

## Alcance de la conclusión

La consulta adicional por empresa es un defecto real y corregido. **No se ha demostrado que explique por sí sola los errores de transporte del ensayo remoto.** La ruta de sesión, con una sola consulta, también sufrió latencia alta. Conexiones nuevas, arranques de funciones, espera de recursos y transporte siguen siendo hipótesis que requieren métricas del servidor y un ensayo posterior.

Los contadores de SELECT se midieron en SQLite temporal, sin conexión de red. No representan la latencia ni la concurrencia de PostgreSQL/Vercel. No se aumentaron los tiempos de espera para ocultar el fallo. Una repetición remota deberá documentarse aparte, manteniendo los mismos límites y conservando este resultado original.

## Repetición posterior a la corrección

El informe agregado `.vercel/qa-remote-load-20261116-after.json` conserva el resultado de la repetición con los mismos límites de solicitudes, tiempo de espera y datos. El marcador identifica el mismo origen de QA sin mostrarlo en claro.

| Concurrencia | Intentos registrados | Errores | p50 | p95 | Resultado |
| --- | --- | --- | --- | --- | --- |
| 1 | 19 de 100 | 1 de transporte | 477,73 ms | 10.001,92 ms | Detenido al detectar el error |
| 5 | No ejecutado | No medido | No medido | No medido | El primer escenario no completó |

Hubo 18 respuestas HTTP 200 y un fallo de transporte en la lista pública de ofertas. Sesión y recomendaciones registraron seis respuestas correctas cada una; sus p95 fueron 1.297,76 ms y 559,42 ms. El escenario duró 19,502 segundos y quedó incompleto. La muestra parcial de 19 solicitudes no permite comparar capacidad ni distribuciones de latencia como si fueran dos ensayos completos y controlados.

Los percentiles globales incluyen los intentos fallidos y su tiempo transcurrido. En esta repetición, el p95 global coincide con el único fallo de diez segundos; no es el p95 de las respuestas HTTP exitosas exclusivamente.

La eliminación del N+1 permanece verificada por los contadores de consultas, pero **no resolvió la inestabilidad HTTP observada**. No se declara aprobado el rendimiento del entorno ni se atribuye a ese cambio la variación entre ensayos.

## Diagnóstico siguiente, sin repetir carga a ciegas

1. Conservar ambos informes y dejar abierta la incidencia. No aumentar el tiempo de espera del cliente ni el tamaño del pool para hacer desaparecer errores de las métricas.
2. Clasificar el fallo de transporte sin registrar el texto de la excepción, URL, JWT ni credenciales. El runner actual agrupa todas las excepciones `httpx.HTTPError` en `transport_error`, por lo que no distingue espera de conexión, espera de lectura, protocolo o pool del cliente. Conservar únicamente el nombre de clase permitido y metadatos de correlación del ensayo.
3. Correlacionar las solicitudes con los registros existentes de Vercel en las ventanas de ambos informes: existencia de invocación, región, duración, arranque de función y estado de terminación. Una solicitud que no llegó a la función exige un diagnóstico distinto de una función que terminó después de diez segundos o respondió correctamente antes del fallo del cliente.
4. Revisar métricas de Neon para esas mismas ventanas: arranque de cómputo, conexiones, espera y recursos. Las regiones informadas por el operador son API en `iad1` y Neon en `sa-east-1`; su separación es una hipótesis de latencia, no una explicación demostrada del fallo de diez segundos. La posibilidad y costo de acercar la función a `gru1` se deben comprobar en la cuenta antes de modificar el despliegue.
5. Si hace falta instrumentación, limitarla a QA: separar tiempos de adquisición/conexión a la base, ejecución SQL y procesamiento de la respuesta. No publicar datos de consultas ni parámetros. No agregar un endpoint público con información de infraestructura.
6. Tras obtener esa clasificación, acordar un único cambio y una sola repetición acotada con los mismos límites. Preverificación correcta y arranque de un worker no garantizan que nuevas instancias concurrentes estén calientes. Detener al primer fallo y registrar el resultado aunque no complete el escenario.

La revisión estática no mostró una fuga evidente de sesiones: `get_db` usa un administrador de contexto para cerrarlas. Tampoco demuestra agotamiento del pool, errores TLS o problemas de conexiones de la base; el ensayo serial incompleto no permite deducirlos. Esas causas deben mantenerse como hipótesis hasta contar con evidencia del tramo que falla.
