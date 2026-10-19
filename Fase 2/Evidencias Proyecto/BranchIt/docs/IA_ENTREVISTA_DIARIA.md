# IA: preparación de postulaciones y entrevista diaria

Gemini ya estaba conectado mediante `/assistant/chat` para presentación y entrevista. Esta actualización añade el modo `postulacion`, con la oferta seleccionada como contexto. Distingue requisitos expresos de sugerencias y pide un resumen anonimizado si necesita conocer las habilidades del egresado; no envía automáticamente el perfil privado a Google.

## Compatibilidad visual

El hub ordena las ofertas por coincidencias reales del perfil y muestra un anillo pequeño con porcentaje solo en las primeras 10 que tengan coincidencias. La fórmula comparte las reglas de afinidad de postulantes: carrera afín aporta 20 puntos; cada habilidad o tecnología de proyecto mencionada en la oferta aporta 40, hasta 80. No es una estimación estadística de contratación ni una puntuación generada por Gemini. Los empates se resuelven por cantidad de coincidencias y el orden existente de publicación.

## Una entrevista al día

- Una sesión por cuenta y día calendario en `America/Santiago`; incluye 5 preguntas y una respuesta final de retroalimentación (6 turnos del modelo).
- La advertencia se muestra antes de comenzar. La sesión puede retomarse desde otro dispositivo, recuperando su historial cifrado.
- El límite se comprueba en el servidor. Un bloqueo de la fila de usuario y la restricción única `(usuario_id, fecha)` evitan crear sesiones paralelas en distintos workers de Vercel.
- El cliente no controla el historial de entrevista: el servidor utiliza la copia guardada. No permite cambiar la oferta de una sesión.
- Una generación fallida no crea la sesión ni aumenta sus turnos. Una respuesta exitosa consume el turno aunque el cliente pierda la conexión; se puede recuperar desde el estado del asistente.
- Presentación y consultas de requisitos no consumen la entrevista diaria. No se añadió un límite diario propio a esos dos modos; se mantienen las cuotas y errores del proveedor.
- Las sesiones terminadas o de días anteriores no admiten más turnos. Si la oferta se cierra, no se continúa la entrevista sobre esa oferta.

Se añadió `tzdata` para que Windows y Vercel calculen el día con la misma zona horaria.

## Migración y publicación

`0008_entrevista_diaria` crea `entrevistas_ia`, sin modificar cuentas, ofertas ni postulaciones. Se aplicó y verificó en Neon BranchIt/main/neondb: 13 usuarios, 100 ofertas y 1 postulación conservados, 0 sesiones iniciales y restricción única presente. El SQL equivalente está en `backend/scripts/0008_entrevista_diaria_neon.sql`.

Queda subir los archivos a GitHub y desplegar frontend/backend en Vercel. La disponibilidad informada por `/assistant/status` indica que existe una clave configurada; no realiza una llamada de salud al proveedor ni garantiza cuota disponible.

## Verificación

Suite de backend correcta, con casos nuevos de límite diario, recuperación, historial manipulado, aislamiento de cuentas, cierre de sesión, día siguiente, fallo del proveedor sin consumo y primeras 10 compatibilidades. Migraciones verificadas en SQLite y SQL generado para PostgreSQL. Lint y build correctos. Se comprobó visualmente el hub, el acceso desde la oferta al modo de requisitos y la advertencia diaria con datos ficticios; no se hicieron llamadas reales a Gemini durante esas pruebas.

Para completar la validación funcional de IA en producción, revisar respuestas reales en varias categorías y comprobar que los requisitos citados correspondan a cada oferta. Esta integración utiliza instrucciones y contexto de oferta; no entrena un modelo propio.
