# Sprint 5 — Ofertas y presentación

## Empresa

Puede crear, leer y editar sus ofertas, incluyendo título, descripción,
requisitos, ubicación y modalidad. Puede cerrar/reabrir la recepción de
postulaciones y eliminar ofertas que todavía no tengan postulaciones.
El backend impide modificar ofertas de otra empresa.

Las ofertas con postulaciones no se eliminan: se cierran para conservar
antecedentes. La API devuelve 409 y la interfaz explica esa alternativa.
Los envíos de formularios se deshabilitan mientras se guardan los cambios.

## Egresado

Puede crear su presentación al guardar por primera vez, leerla en la vista
previa, modificarla y eliminar solo el texto de presentación. La eliminación
ya no borra la cuenta ni los demás datos del perfil. Las postulaciones previas
conservan la presentación enviada en ese momento.

Puede consultar ofertas abiertas, filtrar por cargo/empresa, ubicación y
modalidad, abrir sus detalles y acceder a la postulación del sprint 6.

## Evidencia

- `evidencias/gestion-ofertas.png`
- Pruebas CRUD, propiedad y conservación de cuenta/postulaciones en
  `backend/tests/test_flows.py` y `backend/tests/test_sprints.py`.
