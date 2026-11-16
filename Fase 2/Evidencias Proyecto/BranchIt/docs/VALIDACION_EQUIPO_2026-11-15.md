# Validación del equipo · 15 de noviembre de 2026

## Alcance autorizado

Esta iteración valida la aplicación con el equipo y cuentas ficticias. El usuario decidió aplazar el piloto con personas externas. Ese piloto no se presenta como realizado ni como un bloqueo de las comprobaciones autorizadas ahora. La revisión interna tampoco se presenta como auditoría de seguridad independiente o certificación de accesibilidad.

## Baseline ejecutado

Las comprobaciones iniciales se realizaron antes de cerrar los cambios de esta iteración; no sustituyen la ejecución final sobre el código integrado.

| Comprobación | Resultado inicial |
| --- | --- |
| `python -W ignore -m unittest discover -s tests -q` | 84 casos, correctos; 75,561 s. Base de pruebas aislada. |
| `npm run lint` | Correcto, sin errores. |
| `npm run build` | Correcto; 5,33 s. Persiste una advertencia de tamaño del bundle, no un error de compilación. |

El primer intento de compilación dentro del aislamiento falló porque esbuild no pudo leer directorios superiores en Windows. El mismo comando terminó correctamente al ejecutarse con el permiso correspondiente; no se modificó el código para ocultar ese fallo del entorno. Los registros privados están en `.vercel/qa-*-baseline-2026-11-15.log` y no contienen un volcado de las variables del servidor.

## Regresión integrada observada

Después de integrar las funciones nuevas se ejecutó la suite completa del backend: **106 casos correctos en 82,147 segundos**. El registro privado es `.vercel/sprint11-backend-tests.txt`. También resultaron correctos los tres casos Node del retorno de pago. Estos resultados amplían el baseline inicial; no acreditan por sí solos el recorrido real del proveedor de pagos, la carga HTTP ni la interacción del navegador.

En la revisión posterior del 16 de noviembre se observaron **110 pruebas backend correctas en 111,194 segundos** y **nueve casos Node correctos** (tres del retorno y seis del control de intentos de pago). Después se añadió una prueba de diagnóstico seguro al harness: sus ocho casos terminaron correctamente en 0,009 segundos, sin conexiones. La nueva prueba queda pendiente de incluir en el siguiente conteo de la suite completa; no se suma por adelantado a una ejecución que todavía no ocurrió. El lint y la compilación terminaron correctamente en la comprobación de los archivos revisados; la comprobación conjunta final se registrará aparte cuando concluya.

## Carga HTTP preparada para PostgreSQL de ensayo

`backend/scripts/load_preview.py` permite medir solicitudes HTTP de lectura a una API **aislada**, a diferencia del ensayo ASGI/SQLite histórico. No crea cuentas, no prepara la BD y no llama a Gemini, Blob o pagos.

Antes de enviar el JWT del egresado, exige HTTP 200 en `/health/ready` y el encabezado `X-BranchIT-QA-Run` igual al identificador del manifiesto. El servidor de QA debe emitirlo únicamente cuando se acredite una base PostgreSQL cuyo nombre empieza por `branchit_qa_`. Un simple origen que termina en Vercel no prueba aislamiento: también se exige el marcador y el manifiesto aprobado.

Guardias de la herramienta:

- Origen exacto declarado en un manifiesto privado: solo `localhost`, `127.0.0.1` o una URL HTTPS única de preview de Vercel. Se rechazan los alias públicos conocidos, URLs con credenciales, rutas o parámetros y dominios de rama.
- No sigue redirecciones ni proxies del entorno. El token se conserva en memoria a partir de `QA_GRADUATE_TOKEN`, sin imprimirlo ni guardarlo. El bypass opcional se lee de `QA_VERCEL_BYPASS` y no se incluye en el informe.
- Máximo 300 solicitudes por escenario, hasta 10 workers, hasta 10 solicitudes por segundo globales, timeout máximo de 10 segundos y presupuesto temporal de 60 segundos por escenario. El comando propuesto usa 100 solicitudes a concurrencias 1 y 5.
- Al primer error de transporte, estado HTTP o contenido se detiene la carga; no hay reintentos automáticos. Si hay solicitudes concurrentes en curso, terminan con su timeout y se registran.
- Las únicas rutas medidas son el listado público de ofertas, la identidad del egresado ficticio y sus recomendaciones. Se valida la cuenta esperada y la cantidad exacta de ofertas, no solo el HTTP 200.
- El JSON incluye métricas agregadas y un hash del origen, sin URL privada, JWT, cabeceras, credenciales o contenido de respuestas.

Manifiesto de ejemplo **sin valores utilizables**, para completar en una ubicación privada fuera de la entrega:

```json
{
  "origin": "https://<preview-unica>.vercel.app",
  "target": "preview",
  "database": "postgresql_isolated",
  "qa_run_id": "<uuid-hexadecimal-de-32-caracteres>",
  "graduate_id": 0,
  "expected_offers": 100
}
```

Desde `backend`, después de que el responsable haya creado y verificado el entorno aislado y proporcionado el token de prueba por un medio privado:

```powershell
.\.venv\Scripts\python.exe scripts/load_preview.py --manifest <archivo-privado.json> --requests 100 --concurrency 1 5 --output ..\.vercel\qa-preview-load-2026-11-15.json
```

El ejemplo no funciona sin completar los valores y acreditar el servidor de ensayo. No se debe sustituir el origen por la API pública. La carga remota queda pendiente hasta observar su ejecución y registrar las métricas; preparar el script no equivale a haberla realizado.

Se ejecutaron seis pruebas aisladas de las guardias del runner mediante transporte simulado, sin abrir conexiones: rechazo de producción y dominios ajenos, ausencia de JWT antes del marcador QA, rechazo de redirecciones, detección de fixtures incorrectas, límites del presupuesto y parada al primer error. El resultado fue correcto. Estas pruebas verifican el control del generador de carga, no el rendimiento de la aplicación desplegada.

El runner se amplió para distinguir errores de transporte mediante etiquetas de una lista fija, como `ReadTimeout`, `ConnectTimeout` o `RemoteProtocolError`. Los resúmenes incluyen el contador `transport_errors`; nunca se serializa el mensaje de la excepción, la URL ni sus cabeceras. Una prueba simula una excepción con datos privados en el mensaje y verifica que no aparecen en el informe. No se ejecutó carga remota como parte de esa prueba.

## Primera carga remota observada el 16 de noviembre

Se acreditó un entorno PostgreSQL separado con 100 ofertas y 11 usuarios ficticios, migrado hasta `0013`. El rol de ensayo no puede leer la tabla `usuarios` de producción. Las solicitudes midieron únicamente las rutas de lectura acordadas. No se hicieron llamadas de carga a pagos, Gemini o Blob ni escrituras sobre los datos de producción.

| Concurrencia | Solicitudes observadas / previstas | Errores | p50 | p95 | Solicitudes por segundo | Resultado |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 100 / 100 | 0 | 187,41 ms | 413,16 ms | 3,52 | Completo |
| 5 | 36 / 100 | 2 de transporte | 235,63 ms | 9.823,78 ms | 3,25 | Detenido; no aprobado |

El límite de espera fue de diez segundos. Al aparecer los errores se detuvo el segundo escenario, respetando las solicitudes que ya estaban en curso. Su p95 incluye las demoras del ensayo interrumpido y no debe leerse como un resultado satisfactorio. El registro agregado está en `.vercel/qa-remote-load-20261116.json`, sin URL privada, tokens ni contenido de respuestas.

**Incidencia abierta:** las consultas concurrentes presentaron esperas cercanas al timeout. La causa y una posible corrección están en investigación; no se atribuye todavía a PostgreSQL, Vercel o al código sin evidencia. El ensayo debe repetirse después del diagnóstico. El resultado de concurrencia 1 no permite aprobar el escenario de concurrencia 5 ni establecer capacidad de producción.

### Repetición después de reducir las consultas SQL

Se corrigió un N+1 confirmado en los listados de ofertas, usando la relación de empresa ya incluida en el JOIN. Con 100 ofertas y diez empresas, las consultas SELECT medidas localmente pasaron de 11 a 1 en el listado público y de 13 a 3 en recomendaciones. La incidencia y la prueba de presupuesto de consultas se describen en `docs/INCIDENCIA_RENDIMIENTO_QA_2026-11-16.md`. El conteo local no mide latencia remota y no demuestra que el N+1 fuese la única causa.

La repetición HTTP posterior, conservada en `.vercel/qa-remote-load-20261116-after.json`, se detuvo con concurrencia 1 después de 19 de las 100 solicitudes previstas: 18 respuestas 200 y un error de transporte; p50 477,73 ms y p95 10.001,92 ms. No se inició el escenario de concurrencia 5. **Tampoco se aprueba esta repetición.** El diagnóstico acotado con el nuevo contador de tipos de transporte queda pendiente; no se aumentó el timeout para ocultar el fallo.

## Revisión interna de Webpay de integración

La revisión de lectura del código y sus casos de prueba comprobó que el precio se fija en el servidor, que el resultado del proveedor debe coincidir con la orden y sesión, y que solo `AUTHORIZED` con código entero cero puede aplicar el beneficio. El token se conserva cifrado, el recibo exige la cuenta propietaria y los reintentos utilizan una referencia idempotente. La vigencia y la aplicación del beneficio se guardan juntas bajo bloqueo de las filas de cuenta y orden.

La implementación apunta exclusivamente al entorno de integración y valida el destino exacto del formulario. No habilita la API productiva de Transbank. Los casos de error incluyen cancelación, expiración, monto u orden distintos, retorno repetido, pérdida de respuesta de confirmación y recuperación mediante consulta del proveedor. Una intención de creación antigua sin token se presenta como incierta, sin repetir automáticamente la creación del pago.

La revisión inicial de lectura no hizo cobros, no utilizó tarjetas reales ni contactó Transbank. El ensayo posterior con el proveedor de integración se documenta a continuación. También debe comprobarse que la duración permitida de la función de Vercel cubra los timeouts del protocolo; en un caso de confirmación incierta pueden ocurrir tres llamadas consecutivas de hasta diez segundos. La recuperación del estado no debe sustituirse por una activación desde el navegador.

## Webpay observado en integración el 16 de noviembre

El recorrido de navegador utilizó la tarjeta oficial de prueba en `webpay3gint.transbank.cl`, pasó por el banco ficticio y retornó a la aplicación. Se observó el mensaje «Pago de prueba autorizado. Tu suscripción está activa» y una vigencia hasta el 16 de diciembre de 2026. El importe fue 2.990 CLP. **No se efectuaron cobros reales ni se habilitó el proveedor productivo.**

La captura se conserva en `docs/evidencias/webpay-autorizado-integracion-2026-11-16.png`. La comprobación del estado en PostgreSQL ejecutó tres callbacks concurrentes y obtuvo tres respuestas 303, una sola orden con el beneficio aplicado y la misma fecha de vencimiento después de repetir el retorno. El agregado privado `.vercel/webpay-real-20261116.json` registra estos resultados sin tokens de pago, datos de tarjeta ni datos personales. Es un ensayo puntual de idempotencia con PostgreSQL, no una prueba de capacidad del proveedor.

La cancelación y la confirmación incierta tienen cobertura automatizada. Este registro no afirma que se observaron también esos dos recorridos en un navegador contra el proveedor real de integración.

## Accesibilidad observada por el equipo el 16 de noviembre

Se comprobó el primer Tab hacia el enlace para saltar al contenido. Al enviar el inicio de sesión vacío, el foco se dirigió al primer campo obligatorio. En una vista de 320 px no se observó desbordamiento horizontal; el ancho del documento medido fue de 305 px. Después del retorno de pago, el foco automático llegó al encabezado del recibo. Estas observaciones no sustituyen una prueba con lector de pantalla ni acreditan conformidad completa WCAG 2.1.

## Registro de QA del equipo

El responsable de la sesión registra el escenario, rol, resultado observado e incidencia. Usar códigos de prueba y datos ficticios; no nombres de participantes, RUT, contraseñas o documentos reales. Las filas siguientes son una plantilla, no participantes ni resultados inventados.

| Escenario | Rol | Resultado por registrar | Evidencia / incidencia |
| --- | --- | --- | --- |
| Navegación por teclado, foco y errores de formularios | Acceso del egresado | Enlace de salto y foco del primer obligatorio observados | No se amplía a formularios no recorridos. |
| Perfil, portafolio público y privacidad del contacto | Egresado | Pendiente de sesión del equipo | — |
| Oferta, preguntas, postulación y antecedentes | Ambos | Pendiente de sesión del equipo | — |
| Contratación, bloqueo de postulaciones y finiquito PDF ficticio | Ambos | Pendiente de sesión del equipo | — |
| Suscripción y retorno de Webpay de integración | Egresado ficticio | Autorización y recibo observados | Captura indicada; sin cobros productivos. |
| Vista de 320 px | Pantalla recorrida de QA | Sin desbordamiento horizontal | Documento de 305 px; no cubre todas las vistas. |
| Zoom y lector de pantalla | Ambos | Pendiente de sesión específica | No se declara certificación. |
| IA con contenido ficticio, respetando cuotas del proveedor | Egresado | Pendiente de sesión específica | Sin usar datos personales. |

Registrar por tarea: fecha, navegador, ancho o zoom cuando corresponda, rol de cuenta ficticia, pasos, resultado esperado, resultado observado, gravedad y captura anonimizada. Las tareas fallidas se repiten después de la corrección. No completar automáticamente las celdas por el solo hecho de que existan pruebas unitarias.

## Cierre y límites

La regresión final, la revisión de seguridad del pago y las comprobaciones de navegador se incorporarán cuando terminen los cambios y sus responsables entreguen evidencia. La carga sobre PostgreSQL mide solo el escenario, datos y cuota acordados; no establece capacidad máxima ni un SLA de producción. El piloto externo se mantiene aplazado por decisión del usuario, y una auditoría independiente permanece sin realizar.
