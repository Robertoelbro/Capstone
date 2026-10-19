# Diagrama de base de datos de BranchIT

Generado el 19 de octubre de 2026 desde `backend/app/models.py`. Representa las 8 tablas de aplicación y sus 10 claves foráneas, correspondientes al esquema hasta `0008_entrevista_diaria`. No se consultaron registros ni credenciales de Neon. No es una extracción en vivo: refleja los modelos actuales del proyecto.

- `branchit.html`: visor local con zoom.
- `branchit.png`: imagen para presentaciones.
- `branchit.svg`: imagen vectorial ampliable sin pérdida de calidad.
- `branchit.mmd`: fuente editable en Mermaid.
- `branchit.sql`: DDL PostgreSQL de referencia, NO ejecutar sobre una base existente.
- `branchit.schema.json`: inventario de columnas y claves.

Se excluyen `alembic_version` y los esquemas de respaldo. Las flechas del dibujo van desde la tabla que contiene la FK hacia la tabla referenciada.

Los perfiles de egresado y empresa se vinculan mediante `usuario_id` único. El tipo de cuenta y la aplicación determinan qué perfil corresponde a cada usuario. La FK de foto de empresa es opcional; la propiedad del archivo se valida en la API. Borrar una oferta deja nula su referencia en entrevistas IA (`ON DELETE SET NULL`).

Las experiencias laborales, habilidades, proyectos, certificaciones y enlace al título están dentro del JSON `perfiles_egresado.portfolio`, por lo que no aparecen como tablas independientes. Los binarios de fotos, videos y documentos se almacenan en Vercel Blob; `archivos_portfolio` conserva sus metadatos. Las respuestas y antecedentes de la postulación se guardan en `postulaciones.datos_cifrados`, y la conversación de entrevista en `entrevistas_ia.datos_cifrados`.

## Fuente editable

```mermaid
erDiagram
    usuarios ||--o| perfiles_egresado : tiene
    usuarios ||--o| perfiles_empresa : tiene
    usuarios ||--o{ archivos_portfolio : posee
    usuarios ||--o{ notificaciones : recibe
    usuarios ||--o{ entrevistas_ia : practica
    perfiles_empresa ||--o{ ofertas_empleo : publica
    perfiles_egresado ||--o{ postulaciones : envia
    ofertas_empleo ||--o{ postulaciones : recibe
    ofertas_empleo |o--o{ entrevistas_ia : contextualiza
    archivos_portfolio |o--o{ perfiles_empresa : foto_opcional
    usuarios {
        INTEGER id PK
        VARCHAR_12 rut UK "nullable"
        VARCHAR_30 telefono "nullable"
        DATE fecha_identidad "nullable"
        VARCHAR_255 email UK
        VARCHAR_255 password_hash
        tipousuario tipo
        TIMESTAMP_WITHOUT_TIME_ZONE fecha_registro
        BOOLEAN activo
        INTEGER token_version
    }
    archivos_portfolio {
        VARCHAR_32 id PK
        INTEGER usuario_id FK
        VARCHAR_20 tipo
        VARCHAR_180 nombre
        VARCHAR_80 mime
        INTEGER tamano
        INTEGER duracion "nullable"
        VARCHAR_255 pathname UK
        BOOLEAN verificado
        TIMESTAMP_WITHOUT_TIME_ZONE creado
    }
    notificaciones {
        INTEGER id PK
        INTEGER usuario_id FK
        VARCHAR_400 mensaje
        VARCHAR_200 destino
        BOOLEAN leida
        TIMESTAMP_WITHOUT_TIME_ZONE creada
    }
    perfiles_egresado {
        INTEGER id PK
        INTEGER usuario_id FK,UK
        VARCHAR_100 nombre
        VARCHAR_100 apellido
        VARCHAR_150 carrera "nullable"
        INTEGER anio_egreso "nullable"
        TEXT presentacion "nullable"
        VARCHAR_255 linkedin_url "nullable"
        VARCHAR_255 foto_url "nullable"
        JSON portfolio
    }
    perfiles_empresa {
        INTEGER id PK
        INTEGER usuario_id FK,UK
        VARCHAR_150 nombre_empresa
        VARCHAR_150 rubro "nullable"
        TEXT descripcion "nullable"
        VARCHAR_255 sitio_web "nullable"
        VARCHAR_255 logo_url "nullable"
        VARCHAR_32 foto_id FK "nullable"
    }
    ofertas_empleo {
        INTEGER id PK
        INTEGER empresa_id FK
        VARCHAR_150 titulo
        TEXT descripcion
        TEXT requisitos "nullable"
        VARCHAR_150 ubicacion "nullable"
        VARCHAR_50 modalidad "nullable"
        TIMESTAMP_WITHOUT_TIME_ZONE fecha_publicacion
        BOOLEAN activa
        JSON preguntas
        INTEGER formulario_version
        VARCHAR_80 categoria
        VARCHAR_80 demo_clave UK "nullable"
        BIGINT sueldo "nullable"
        TEXT funciones "nullable"
        JSON perfiles_deseados "nullable"
        TEXT condiciones_laborales "nullable"
        BOOLEAN adaptada_discapacidad "nullable"
    }
    entrevistas_ia {
        VARCHAR_32 id PK
        INTEGER usuario_id FK
        DATE fecha
        INTEGER oferta_id FK "nullable"
        TEXT datos_cifrados
        INTEGER turnos
    }
    postulaciones {
        INTEGER id PK
        INTEGER oferta_id FK
        INTEGER egresado_id FK
        TIMESTAMP_WITHOUT_TIME_ZONE fecha_postulacion
        TEXT datos_cifrados
        BOOLEAN seleccionada
    }
```
