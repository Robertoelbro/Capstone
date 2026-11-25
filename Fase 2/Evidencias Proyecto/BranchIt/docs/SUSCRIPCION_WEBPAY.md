# Suscripción mensual y Webpay de integración

Precio definido: **$2.990 CLP por mes**, para egresados. La integración transaccional se implementó y se probó con Transbank en su entorno de integración el 16 de noviembre de 2026, usando exclusivamente tarjetas ficticias. La API productiva de Transbank permanece bloqueada en esta versión. La disponibilidad del checkout de prueba depende de la configuración privada de cada entorno.

Se comprobó autorización, activación de un mes calendario y tres retornos concurrentes del mismo pago en PostgreSQL, sin extender la vigencia otra vez. La migración `0013_pagos_webpay` incorpora órdenes persistentes con tokens cifrados y una referencia de idempotencia por usuario. Consultar el [registro de publicación](DESPLIEGUE_2026-11-16.md) para el estado de la página principal. Las secciones siguientes conservan el diseño inicial y las condiciones de una futura habilitación productiva; no describen una ausencia actual de código transaccional.

Beneficios definidos: prácticas de entrevista sin límite diario propio de BranchIT y condición de candidato destacado en las postulaciones. Las cuotas y límites del proveedor de IA siguen aplicando; no se promete disponibilidad ilimitada de Gemini. La empresa no recibe el motivo comercial de un destacado. La validación de los beneficios utiliza `has_subscription(db, usuario_id)` en el servidor, que exige estado activo y vigencia futura.

## API disponible

- `GET /billing/me`: exige sesión de egresado. Devuelve precio, periodicidad mensual, estado efectivo, vencimiento, beneficios, pasarela y disponibilidad del pago.
- `POST /billing/checkout`: exige sesión de egresado y un `request_id` UUID. En un entorno de integración correctamente configurado crea o recupera la misma orden, con monto fijo decidido por el servidor; devuelve HTTP 503 si el entorno no está habilitado.
- `GET/POST /billing/return`: confirma el resultado con Transbank desde el servidor y devuelve al recibo sin incluir el token en la URL del frontend.
- `GET /billing/orders/{id}` y `POST /billing/orders/{id}/reconcile`: consulta privada del titular y recuperación de resultados inciertos.
- No hay endpoint público para marcar una cuenta como pagada, cambiar la vigencia o aceptar un retorno exitoso desde el navegador.

Una suscripción solo se informa activa si su estado almacenado es `activa` y su fecha de vencimiento está en el futuro. Una fila sin fecha o vencida se informa inactiva. Consultar el estado no crea filas ni renueva la vigencia. La migración `0011_suscripciones`, posterior a `0010_empleo_finiquito`, crea el almacenamiento sin activar cuentas existentes.

**La suscripción no evita el bloqueo de postulaciones por experiencia laboral.** No se incorpora como condición alternativa en los permisos de postulación.

## Configuración reservada al servidor

Preparar estas variables únicamente en el backend privado de Vercel, nunca como variables `VITE_*`, en Git ni en mensajes del chat:

| Variable | Uso previsto |
| --- | --- |
| `WEBPAY_COMMERCE_CODE` | Código del comercio del entorno elegido. |
| `WEBPAY_API_KEY` | Clave de API privada del comercio. |
| `WEBPAY_ENV` | Empezar con `integration`; producción se configura después de validar el flujo. |
| `WEBPAY_ENABLED` | Habilita únicamente el checkout de integración cuando vale `true` y las demás variables son válidas. |
| `WEBPAY_RETURN_URL` | URL HTTPS del backend terminada en `/billing/return`. |
| `WEBPAY_FRONTEND_URL` | Origen HTTPS del frontend, también incluido en `CORS_ORIGINS`. |

La configuración exige `WEBPAY_ENV=integration`, comercio y clave válidos, URLs controladas y activación explícita. `WEBPAY_ENV=production` continúa cerrado, incluso con credenciales. Las pruebas automatizadas usan un proveedor simulado; la prueba real del entorno de integración quedó registrada por separado. Ninguna clave debe incluirse en Git.

## Condiciones para una futura habilitación productiva

La [documentación oficial de Webpay Plus](https://transbankdevelopers.com/documentacion/webpay-plus) describe crear la transacción y confirmar su resultado con el proveedor. El retorno del navegador con un `token_ws` por sí solo no acredita un pago. El código actual implementa creación, confirmación y recuperación únicamente para integración. Antes de permitir cobros reales se deben revisar y validar estas condiciones con el comercio y Transbank:

1. Conservar los beneficios ya definidos y precisar vencimiento mensual, renovación manual y condiciones visibles antes del pago. Webpay Plus no implica renovación automática de una suscripción; esta preparación no almacena tarjetas ni autoriza cargos recurrentes.
2. Crear una orden persistente desde el servidor con usuario, monto fijo de 2990, moneda CLP y referencias únicas. No aceptar el precio enviado por el cliente.
3. Crear la transacción en el entorno de integración con timeout y URL de retorno HTTPS controlada. Conservar la relación entre orden y token sin exponer secretos ni datos de tarjeta.
4. En el retorno, consultar/confirmar con Webpay desde el servidor y validar estado autorizado, código de respuesta, monto, orden, token y cuenta vinculada. Tratar cancelación, timeout y respuesta incierta sin activar la cuenta.
5. Activar vigencia en una transacción de base de datos idempotente: repetir el retorno no debe cobrar ni sumar meses. Recuperar transacciones inciertas con consulta al proveedor y conciliación, no con indicadores del navegador.
6. Probar aprobación, rechazo, abandono, expiración, token ajeno, monto u orden distintos y repetición concurrente con tarjetas de integración. Separar estas pruebas de producción.
7. Después de revisar evidencias, configurar producción y habilitar explícitamente el pago. No cargar claves productivas en una vista previa compartida ni registrar tokens/tarjetas en logs.

Para asignar una suscripción administrativa al usuario que el equipo indique más adelante, preparar un procedimiento restringido e identificable después de confirmar cuenta y vigencia. No existe una ruta de autoactivación ni se ha activado ninguna cuenta con esta entrega.

## Verificación

`backend/tests/test_billing.py` comprueba sesión y rol, aislamiento entre cuentas, vigencia expirada o ausente, ausencia de secretos en respuestas y rechazo de activación mediante parámetros del navegador. No utiliza Webpay real, claves reales ni datos de producción.
