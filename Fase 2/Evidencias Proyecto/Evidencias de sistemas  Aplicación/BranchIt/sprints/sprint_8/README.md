# Sprint 8 · Contratación, finiquito y seguimiento

Política actualizada el 9 de noviembre de 2026. Sustituye la reanudación mediante un simple cambio de selector de la primera versión.

## Recorrido

1. La empresa cierra una convocatoria seleccionando un finalista y su fecha de inicio. La contratación se registra en el seguimiento privado del egresado. Cerrar sin candidato no registra empleo.
2. El egresado contratado no puede enviar nuevas postulaciones. Puede consultar y compartir ofertas, conservar su portafolio e historial y utilizar IA. Los demás candidatos solo ven la convocatoria cerrada.
3. Al terminar el empleo por renuncia o despido, presenta su propio PDF privado de hasta 5 MB y declara la fecha de término. El prototipo valida formato y propiedad del archivo, no autenticidad, identidad o contenido legal del finiquito.
4. Si el empleo duró menos de un año calendario se reactiva la búsqueda. Si llegó al primer aniversario o lo superó, las nuevas postulaciones quedan bloqueadas. Se conserva el acceso al portafolio y a la IA. La suscripción no evita ese bloqueo.

El aniversario del 29 de febrero se considera el 28 de febrero del año siguiente. La regla se evalúa sobre ese empleo, no sumando otros períodos. Una vez alcanzado el límite no se elimina al declarar otro empleo.

## Integridad y privacidad

- La API, no el navegador, comprueba los permisos. Un `PUT /employment/me` no puede liberar una contratación vigente sin PDF ni alterar la fecha original del reclutador.
- `POST /employment/release` exige archivo propio, verificado, tipo `finiquito`, MIME PDF, tamaño permitido y fechas coherentes. Un documento ya utilizado no respalda un segundo empleo.
- El historial y los documentos referenciados se conservan cifrados. Los finiquitos nunca se publican en el portafolio ni se comparten con reclutadores; las solicitudes de borrado/sobrescritura de documentos vinculados se rechazan.
- Reabrir una oferta o cambiar el finalista no elimina contrataciones anteriores. Repetir el mismo cierre no duplica ni reactiva un empleo terminado.
- Se mantiene la desactivación de cuenta con contraseña: revoca sesiones, oculta perfil y cierra ofertas empresariales, sin borrar datos ni reactivar automáticamente.

## API y esquema

`GET/PUT /employment/me`, `POST /employment/release`, `PUT /api/employment/jobs/{id}/closure` y `POST /auth/deactivate`. Las ofertas compartibles usan `/ofertas/{id}` en el frontend y el detalle público existente de la API.

`0009` incorpora seguimiento; `0010` añade el límite de experiencia; `0011` prepara suscripciones y `0012` permite entrevistas múltiples para suscriptores. [Resultado de Neon y pruebas](../../docs/CONTRATACION_FINIQUITO_2026-11-09.md).

El flujo anterior de confirmación manual permanece para empleos externos, pero también exige fecha y finiquito para terminar. Los registros antiguos sin fecha pueden indicar su inicio una vez al presentar el documento.

## Evidencias

- Pruebas de seguimiento y desactivación, contratación automática, privacidad, finiquitos, fechas, aniversario exacto, permanencia del bloqueo e idempotencia del cierre.
- [Formulario de contratación y PDF](../../docs/evidencias/seguimiento-finiquito.png).
- [Neon migrado](../../docs/evidencias/neon-0012.png).
- Las capturas de `evidencias/` conservan la primera versión histórica; sus mensajes de reanudación simple no describen la política actual.
