# Antecedentes y orden de postulantes

El editor del egresado permite guardar hasta 20 experiencias laborales de cualquier tipo, incluidas aquellas que no requieren título. Cada entrada contiene cargo, empresa o lugar, fecha de inicio, término opcional y funciones/aprendizajes (hasta 2000 caracteres). Fechas futuras y términos anteriores al inicio se rechazan. También admite un enlace HTTP/HTTPS al título profesional. Ambos se muestran en el portafolio cuando el egresado decide publicarlo.

Al enviar una nueva postulación se guarda una copia cifrada de habilidades, tecnologías de proyectos, certificaciones, experiencias, disponibilidad y enlace al título. El consentimiento del formulario enumera los antecedentes que se compartirán. Cambiar después el perfil no altera esa copia. Para postulaciones anteriores sin copia se muestran los datos actuales, con una indicación explícita en pantalla.

La empresa puede abrir el portafolio publicado desde la ficha del postulante. Si no está publicado se indica esa situación, sin forzar su publicación ni habilitar acceso a archivos privados.

## Afinidad explicable

Solo las empresas propietarias de una oferta pueden consultar sus postulantes. El backend ordena la lista completa antes de que el frontend la divida en grupos de 10.

- Carrera en el área o perfiles deseados de la oferta: 20 puntos.
- Cada habilidad o tecnología de proyecto cuyo nombre aparezca en el título, información del cargo, requisitos o funciones: 40 puntos, con un máximo de 80.
- Se ignoran mayúsculas y acentos, se eliminan duplicados y se respetan límites de palabra (por ejemplo, `Go` no coincide dentro de `Django`).
- Los empates se resuelven por cantidad de coincidencias y después por fecha de postulación más antigua e ID.
- Se destaca como «Candidato destacado» hasta a los primeros 10, siempre que tengan alguna coincidencia. Sin coincidencias no se otorga la etiqueta.

La pantalla muestra los puntos, las habilidades coincidentes y si la carrera es afín. Los puntos son una regla de ordenación, no una probabilidad de éxito ni una evaluación de capacidades. No se usan foto, nombre, RUT, edad, sexo, teléfono ni otros datos personales para ordenar. No se rechaza a nadie automáticamente; la empresa conserva la evaluación y selección final. Las experiencias se muestran como antecedentes para revisión humana; no suman puntos.

## Foto de empresa y publicación

Las ofertas, recomendaciones, formulario y lista de postulaciones del egresado muestran la foto actual de la empresa. Si no existe se usa su logo externo o iniciales. Solo la foto verificada que esté guardada actualmente en el perfil de una empresa activa se puede leer públicamente. Las reservas, otras imágenes y acciones de borrar/subir mantienen la comprobación de propietario.

Estos campos usan el JSON de portafolio y el contenido cifrado de postulaciones existentes: no requieren una nueva migración. Sigue pendiente aplicar `0007_notificaciones` si aún no se aplicó el cambio anterior. Publicar frontend y backend juntos para que la vista de postulantes reciba los nuevos campos.
