# Menú de empresa, cierre y selector telefónico

- Menú con `Crear oferta laboral` (`/ofertas-empresa/nueva`) y `Ver ofertas creadas` (`/ofertas-empresa`). Las ofertas existentes y sus enlaces se conservan. Al publicar se vuelve al listado; se puede editar desde él.
- Cada oferta permite cerrar la convocatoria seleccionando una postulación propia, o indicando explícitamente que se cierra sin seleccionar candidato. La empresa puede consultar o cambiar su selección después del cierre.
- La selección está en `postulaciones.seleccionada`, con índice único parcial que limita a un candidato por oferta. El cierre y la selección se guardan juntos, bajo bloqueo de la oferta. Al reabrirla se limpia la selección anterior.
- Solo la empresa propietaria recibe el campo `seleccionada` al consultar postulantes. El historial del egresado y las ofertas públicas no incluyen ese dato ni el identificador del seleccionado; muestran que la convocatoria se cerró. Las ofertas cerradas no reciben nuevas postulaciones.
- El teléfono muestra banderas SVG locales y prefijos; el país sigue disponible mediante búsqueda, etiquetas accesibles y teclado. No se depende de que Windows dibuje emojis de banderas.
- La reserva del botón IA se aplica dentro del contenido y del footer, evitando la franja vacía al final de la página.

Migración `0006_cierre_convocatorias` aplicada y verificada en Neon el 18 de octubre de 2026: **15 usuarios, 101 ofertas, 3 postulaciones**, sin seleccionar candidatos de producción ni modificar convocatorias reales. En otras bases: desde `backend`, ejecutar `.\.venv\Scripts\python.exe -m alembic upgrade head` con su conexión configurada.

Validación: 32 pruebas de backend, incluyendo aislamiento entre empresas, privacidad para los egresados, rechazo de postulantes de otra oferta, bloqueo de nuevas postulaciones al cerrar, sustitución de selección, índice único y reapertura. Lint y compilación Vite correctos. Recorrido de navegador con datos ficticios locales: selector de bandera, vistas separadas y cierre con candidato.

Los cambios de código quedan locales para que Roberto los publique en GitHub. Deben desplegarse API y frontend en Vercel; Neon ya está actualizado.
