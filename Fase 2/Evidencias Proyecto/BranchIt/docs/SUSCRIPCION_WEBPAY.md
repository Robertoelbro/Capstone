# Suscripción mensual · Preparación de Webpay

Precio definido: **$2.990 CLP por mes**, para egresados. La infraestructura almacena la vigencia y muestra el estado de la cuenta. **No hay cobros habilitados ni una integración transaccional con Webpay terminada**.

Beneficios definidos: prácticas de entrevista sin límite diario propio de BranchIT y condición de candidato destacado en las postulaciones. Las cuotas y límites del proveedor de IA siguen aplicando; no se promete disponibilidad ilimitada de Gemini. La empresa no recibe el motivo comercial de un destacado. La validación de los beneficios utiliza `has_subscription(db, usuario_id)` en el servidor, que exige estado activo y vigencia futura.

## API disponible

- `GET /billing/me`: exige sesión de egresado. Devuelve precio, periodicidad mensual, estado efectivo, vencimiento, beneficios, pasarela y disponibilidad del pago.
- `POST /billing/checkout`: exige sesión de egresado y responde HTTP 503 con un mensaje explícito de que no hubo cobro. No crea transacciones, redirecciones ni suscripciones.
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
| `WEBPAY_ENABLED` | Futuro interruptor explícito de activación; hoy no habilita pagos. |

Estas variables están reservadas para la siguiente implementación; el checkout actual permanece cerrado incluso si existen o si `WEBPAY_ENABLED=true`. Tener las claves no significa que el pago esté operativo. Primero hay que terminar la confirmación segura y validar los beneficios contratados. No se requieren claves para revisar esta pantalla o ejecutar las pruebas actuales.

## Siguiente implementación transaccional

La [documentación oficial de Webpay Plus](https://transbankdevelopers.com/documentacion/webpay-plus) describe crear la transacción y confirmar su resultado con el proveedor. El retorno del navegador con un `token_ws` por sí solo no acredita un pago. Para terminar el flujo:

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
