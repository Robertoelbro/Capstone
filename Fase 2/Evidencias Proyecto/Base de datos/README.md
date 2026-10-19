# Evidencias de base de datos

- [Diagrama e inventario del esquema](Diagrama/README.md): ocho tablas de aplicación y diez claves foráneas, según los modelos hasta `0008_entrevista_diaria`.
- [Diagrama PNG](Diagrama/branchit.png), [SVG](Diagrama/branchit.svg) y [visor local](Diagrama/branchit.html).
- [DDL de referencia](Diagrama/branchit.sql): describe el esquema; no debe ejecutarse sobre una base existente.
- [Modelos SQLAlchemy](../BranchIt/backend/app/models.py).
- [Migraciones Alembic](../BranchIt/backend/migrations/versions/).
- [Instrucciones de despliegue y migración](../BranchIt/docs/DESPLIEGUE_VERCEL.md).

PostgreSQL se aloja en Neon. Este conjunto documenta la estructura y no contiene un respaldo de datos de producción ni credenciales. Los archivos multimedia se almacenan en Vercel Blob. Las migraciones permanecen dentro de la API para conservar su funcionamiento.
