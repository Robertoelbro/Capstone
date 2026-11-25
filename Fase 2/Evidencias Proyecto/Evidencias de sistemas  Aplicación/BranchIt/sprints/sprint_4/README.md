# Sprint 4 — Inicio de sesión y hubs

## Egresado

- Login con validación y redirección a `/hub-egresado`.
- Resumen de oportunidades, postulaciones enviadas y estado de presentación.
- Accesos a presentación, ofertas e historial de postulaciones.
- Últimas postulaciones con empresa y estado recibido.

## Empresa

- Login con redirección a `/hub-empresa`.
- Resumen de ofertas publicadas, abiertas y postulaciones recibidas.
- Accesos a gestión de ofertas y revisión de postulantes.

Ambos hubs requieren sesión y rol correctos. La API comprueba los permisos
independientemente de la navegación del frontend. Se conserva la estética
del template y los textos en español.

## Evidencia

- `evidencias/hub-egresado.png`
- `evidencias/hub-empresa.png`
- Pruebas de login, expiración, cuenta desactivada y revocación en
  `backend/tests/test_flows.py` y `backend/tests/test_sprints.py`.
