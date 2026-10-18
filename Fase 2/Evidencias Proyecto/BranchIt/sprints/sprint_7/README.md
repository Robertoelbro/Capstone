# Sprint 7 — Orientación del egresado con Gemini

Primera integración: Gemini 3.5 Flash-Lite mediante el backend FastAPI.
No requiere migraciones. El usuario administra los commits y pushes de GitHub.

## Funciones

- Botón flotante «Modo IA», exclusivo del egresado; diálogo accesible y adaptable.
- Revisión de un borrador de presentación editable. Copiar la presentación
  guardada solo llena el borrador local; no lo transmite ni cambia el perfil.
- Entrevista de práctica para una oferta activa seleccionada: una pregunta por
  turno, comentarios sobre la respuesta y siguiente pregunta.
- Conversación en memoria de la página. Cerrar el panel conserva el contenido;
  recargar o cerrar sesión lo descarta. Se envían los últimos diez pares de
  mensajes como contexto; esto no es una cuota de consultas por usuario.
- Indicador de respuesta en curso, reintento manual conservando lo escrito,
  manejo de cuota agotada, fallos de configuración y respuestas bloqueadas.
- Respuestas renderizadas como texto, sin ejecutar HTML del modelo.

## Configuración sin contratar un plan

1. Crear un proyecto del nivel Free en Google AI Studio, sin habilitar facturación.
2. Crear una clave para ese proyecto.
3. Guardarla como `GEMINI_API_KEY` en el entorno privado de `branchit-api`,
   Production. Para desarrollo local, usar `backend/.env`.
4. Subir el código de frontend y backend a `Roberto-branch` y desplegar ambos.
   Si la variable se añade después, volver a desplegar el backend.
5. Iniciar sesión como egresado y probar con un borrador ficticio y una oferta demo.

No poner la clave en variables VITE, Git, el navegador ni capturas. El backend
usa exclusivamente `gemini-3.5-flash-lite`; no cambia automáticamente de modelo
ni de proveedor si se agota la cuota. Una clave por sí sola no acredita que la
cuenta sea gratuita: comprobar el nivel de proyecto en AI Studio.

## Datos y alcance

Google solicita no enviar información personal o confidencial al servicio
gratuito. El usuario revisa el texto y confirma que es ficticio o anonimizado.
El servidor omite identificadores conocidos del titular y redacta correos,
teléfonos, RUT y enlaces como defensa adicional; esto no sustituye revisar el
texto libre. El contexto no contiene el perfil completo, archivos, postulaciones,
contraseñas ni claves. En entrevistas solo se agregan campos públicos de la
oferta, que el servidor consulta y exige que siga activa.

El modelo no recibe herramientas de base de datos ni permisos para modificar
el perfil o postular. La práctica no representa una decisión de contratación.
No se implementaron entrenamiento ni cuotas de consultas por usuario. Los
tamaños de solicitud/historial y respuesta están acotados técnicamente; las
cuotas gratuitas del proveedor siguen aplicando.

## Validación

29 pruebas de backend aprobadas, incluidas seis nuevas de IA. Las llamadas al
proveedor se simulan para comprobar permisos, minimización, solicitudes,
conversación, errores y cuotas sin usar tokens reales. Compilación y lint
aprobados. Recorridos locales de revisión y entrevista comprobados con datos
ficticios y respuestas simuladas; panel sin desbordamiento horizontal a 320 px.
La validación real contra Gemini queda pendiente de configurar la clave.

Referencias:
- https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash-lite
- https://ai.google.dev/gemini-api/docs/generate-content/text-generation
- https://ai.google.dev/gemini-api/docs/pricing
- https://ai.google.dev/gemini-api/terms
