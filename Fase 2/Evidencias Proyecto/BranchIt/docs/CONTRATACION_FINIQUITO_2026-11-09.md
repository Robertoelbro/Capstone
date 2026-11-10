# Contratación, finiquito y suscripción · 9 de noviembre de 2026

## Comportamiento entregado

Al cerrar una convocatoria con finalista y fecha de inicio, el reclutador registra la contratación y se bloquean nuevas postulaciones de ese egresado. Los demás postulantes solo reciben el cierre. El titular mantiene portafolio, consulta y enlaces para compartir ofertas, además del asistente de IA.

La salida del empleo requiere un PDF propio de tipo `finiquito`, hasta 5 MB, verificado por el servicio de archivos, fecha de término y motivo. Se acepta cualquier PDF válido para esta demostración: no se interpreta su texto ni se verifica que sea un finiquito auténtico. El archivo permanece privado y se conserva como respaldo del historial cifrado.

Si el empleo terminó antes del primer aniversario de la fecha registrada, vuelve a permitirse postular. Al llegar al aniversario o superarlo se conserva un bloqueo permanente de nuevas postulaciones; no se desactiva la cuenta. En años no bisiestos, el aniversario del 29 de febrero es el 28 de febrero. No se suman períodos de empleos distintos para decidir esta regla. La fecha registrada de la contratación no puede adelantarse mediante la solicitud de término.

Reabrir o cambiar la selección de una convocatoria no borra contrataciones, ni libera a un egresado sin documento. El cierre repetido de una misma contratación es idempotente. Los casos previos de selección de producción no se convirtieron retroactivamente en contrataciones sin conocer su fecha.

## Suscripción

Precio: **$2.990 CLP mensuales**. Beneficios implementados para una vigencia activa:

- Nuevas entrevistas de práctica sin límite diario propio de BranchIT. Cada sesión sigue teniendo cinco preguntas y una devolución final. Se conservan cuotas, disponibilidad y límites técnicos del proveedor.
- Etiqueta «Candidato destacado» en sus postulaciones. Se utiliza la misma etiqueta existente, sin indicar plan, pago, vencimiento o motivo comercial al reclutador. El orden continúa calculándose por afinidad; no se altera la puntuación para aparentar más coincidencias.

El plan gratuito conserva una entrevista diaria. Una suscripción no elimina el bloqueo de postular por contratación o experiencia. No se activó ninguna cuenta de producción: esa asignación se realizará después de identificar al usuario y su vigencia.

[Webpay](SUSCRIPCION_WEBPAY.md) permanece pendiente: pantalla y estado de suscripción preparados; checkout cerrado sin cobros. Falta el flujo transaccional y las credenciales privadas de integración. Añadir una clave por sí solo no activa pagos. No hay almacenamiento de tarjetas ni renovación automática.

## Neon: migración aplicada

Destino comprobado: proyecto **BranchIt**, rama **main**, base **neondb**, proyecto `flat-heart-85887310`, rama `br-cool-dream-b60kngk0`.

Se partió de `0008_entrevista_diaria` y se aplicó hasta **`0012_entrevistas_suscripcion`** mediante el [SQL incremental generado con Alembic](../backend/scripts/0009_0012_neon.sql). Se comprobó revisión y base antes de comenzar. Se usó una transacción, un timeout de bloqueos y comprobación de cantidades antes del commit.

Respaldo interno: esquema `branchit_backup_20261109_migrations`, con versión anterior, entrevista previa y cantidades de control. No se exportaron registros personales ni credenciales. Las migraciones crean seguimiento y suscripciones, agregan el indicador de experiencia y la fecha de creación de entrevistas y sustituyen la unicidad diaria por un índice. El límite gratuito ahora se exige en la API bajo bloqueo de la fila del usuario.

| Verificación | Antes | Después |
| --- | --- | --- |
| Revisión | 0008_entrevista_diaria | 0012_entrevistas_suscripcion |
| Usuarios | 15 | 15 |
| Ofertas | 100 | 100 |
| Postulaciones | 2 | 2 |
| Entrevistas | 1 | 1 |
| Seguimientos | Tabla ausente | 0 filas |
| Suscripciones | Tabla ausente | 0 filas |

También se verificaron `limite_experiencia`, `entrevistas_ia.creada` y la copia de la entrevista anterior en el respaldo. [Captura de la consulta](evidencias/neon-0012.png). No repetir el SQL en la misma base: exige revisión inicial 0008 y fallará si ya está actualizada.

## Verificación de software

- Suite de 74 pruebas completa aprobada, más el caso adicional de suscripción que no elude el límite laboral; los cuatro casos de beneficios se comprobaron juntos. Total: 75 casos distintos verificados.
- Migraciones desde versión inicial con conservación de datos, comparación de modelos, reversión y generación PostgreSQL aprobadas. La reversión de `0012` se detiene si hay entrevistas múltiples para evitar perder historial.
- Lint de frontend y compilación correctos.
- Navegador local con datos ficticios: contratación creada por el cierre, acceso al formulario de PDF, detalle público y compartir visibles, orientación IA accesible y suscripción con precio/beneficios correctos y pago deshabilitado. [Captura del seguimiento](evidencias/seguimiento-finiquito.png), [captura de suscripción](evidencias/suscripcion-webpay-pendiente.png).
- Las pruebas de API verifican propiedad y privacidad de PDFs, fechas, aniversario y bloqueos; los fixtures de prueba de archivos son metadatos aislados. La subida completa a Blob debe comprobarse en un despliegue de ensayo con las funciones de Vercel activas. No se subieron documentos reales durante la revisión local.

La migración de Neon está aplicada; **el código sigue local para que Roberto lo publique en GitHub y despliegue ambos proyectos Vercel**. Después, comprobar `/health/ready` y el recorrido con cuentas de demostración. La llamada real a Gemini y el pago Webpay no se ejecutaron en estas pruebas.
