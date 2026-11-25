# Recomendaciones de certificaciones

El asistente incorpora recursos oficiales cuando prepara una postulación o cuando el egresado pide cursos, formación o certificaciones. En «Preparar postulación» hay un acceso «Pedir sitios para certificarme» que prepara la consulta sin enviarla automáticamente ni saltarse el consentimiento.

Las opciones se seleccionan por los temas de la consulta y de la oferta. Gemini recibe el catálogo como contexto y explica qué habilidades reforzar y qué buscar en cada sitio. No se envía automáticamente el portafolio privado. Si no hay una opción técnica en el catálogo, se indican recursos de habilidades transversales; no se atribuyen certificaciones clínicas o reguladas a esas plataformas.

## Catálogo inicial verificado

- freeCodeCamp: https://www.freecodecamp.org/learn/ — programación, web y datos. Referencia oficial de certificaciones gratuitas: https://github.com/freeCodeCamp/freeCodeCamp/blob/main/README.md
- IBM SkillsBuild: https://skillsbuild.org/adult-learners — formación gratuita y credenciales digitales en los itinerarios correspondientes.
- HP LIFE: https://www.life-global.org/ — negocios, comunicación, marketing y finanzas; formación gratuita con certificado de finalización gratuito.

Referencias consultadas en octubre de 2026. La app informa del tipo de credencial y pide confirmar las condiciones vigentes antes de inscribirse. Un certificado de finalización no se presenta como título, licencia profesional ni garantía de contratación.

## Presentación y enlaces

Los enlaces clicables salen del catálogo del servidor, no de URLs generadas por el modelo. Las respuestas muestran un apartado plegable «Sitios para certificarte», con hasta 3 opciones, su pertinencia, costo del curso y tipo de credencial. Los enlaces de una entrevista se guardan dentro del historial cifrado y se recuperan al retomarla.

El catálogo no navega en vivo por cada conversación y no inventa nombres de cursos, duración ni acreditaciones. Las instrucciones distinguen requisitos reales de la oferta de recomendaciones de formación. Para incorporar otros proveedores se amplía `backend/app/certifications.py` tras verificar sus fuentes oficiales.

No requiere migración de base de datos. Publicar frontend y backend para habilitar la funcionalidad.
