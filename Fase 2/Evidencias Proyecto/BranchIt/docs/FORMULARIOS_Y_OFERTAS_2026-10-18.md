# Formularios y ofertas

Se simplificaron las leyendas decorativas de inicio, paneles y portafolio. Se conservan instrucciones de uso, consentimiento y privacidad; el detalle sobre archivos públicos queda desplegable.

- RUT con puntos, guion y K mayúscula; el servidor conserva la comprobación del dígito verificador.
- Teléfono separado en país/prefijo y número; Chile móvil usa +569 y ocho dígitos agrupados 4 + 4. Se guarda el número completo sin separadores. También se admite Chile fijo y los demás países del catálogo de `libphonenumber-js`.
- Sueldo como entero positivo, fijo mensual bruto CLP, con puntos visibles. Los números se responden en campos de texto con teclado numérico/decimal, sin incremento por rueda o flechas.
- Campos obligatorios con asterisco desde el inicio; al intentar enviar se marcan los campos inválidos en rojo y se conserva la validación nativa del navegador.
- Catálogos de carreras y sectores comerciales en `frontend/src/data/catalogs.js`, buscables sin distinguir acentos/mayúsculas y con normalización ingeniero/ingeniera/ingeniería. "Otros" permite especificar una denominación no incluida. Los sectores son nombres descriptivos, no códigos tributarios del SII.
- Ofertas: sueldo, funciones, información del cargo, uno o más perfiles deseados, condiciones y respuesta Sí/No sobre adaptaciones para discapacidad. Las preguntas del reclutador siguen siendo opcionales.
- Selección única o múltiple con hasta quince opciones editables y botones para agregar/quitar. Respuestas cortas: 200 caracteres; largas: 3.000. Los límites y opciones también se validan en la API.
- Las respuestas múltiples se cifran como listas y se muestran separadas por comas en la revisión de postulaciones.
- Las recomendaciones consideran los perfiles solicitados; las ofertas antiguas mantienen el criterio por categoría.

## Base de datos y publicación

Migración `0005_ofertas_completas` aplicada en Neon, proyecto BranchIt, rama main, el 18 de octubre de 2026. Verificación posterior: **14 usuarios, 101 ofertas y cinco columnas nuevas**. Los registros existentes conservan valores nulos; no se inventan sueldos o condiciones. Para editar su contenido hay que completar los nuevos campos. Se puede cerrar/reabrir una oferta antigua sin completarla.

La migración Alembic está versionada en `backend/migrations/versions/0005_ofertas_completas.py`. En otras bases debe ejecutarse desde `backend`, con `DATABASE_URL` apuntando a la base correspondiente:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
```

**Neon de producción ya está actualizado: no hace falta repetirlo allí.** Roberto publica los cambios en GitHub. Deben desplegarse backend y frontend de la misma rama en Vercel para que se active el formulario nuevo. No se modificaron claves, planes ni conexiones.

## Verificación

Pruebas de API en SQLite aislado, migraciones de ida/vuelta conservando datos, SQL offline para PostgreSQL, validación del frontend y compilación Vite. Prueba de navegador con datos temporales: formato RUT/teléfono, filtro de carreras, errores obligatorios, publicación de oferta con sueldo y preguntas múltiples, y envío de dos opciones desde una cuenta de egresado.
