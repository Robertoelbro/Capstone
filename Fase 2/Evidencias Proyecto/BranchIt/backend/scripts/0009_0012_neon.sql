-- Solo para BranchIt/neondb en revision 0008; incluye respaldo y transaccion.
BEGIN;

DO $guard$
BEGIN
    IF current_database() <> 'neondb' OR (SELECT count(*) FROM public.alembic_version) <> 1
       OR (SELECT version_num FROM public.alembic_version) <> '0008_entrevista_diaria' THEN
        RAISE EXCEPTION 'Base/revision inesperada. No se aplico la migracion.';
    END IF;
END;
$guard$;
SET LOCAL lock_timeout = '10s';
CREATE SCHEMA branchit_backup_20261109_migrations;
CREATE TABLE branchit_backup_20261109_migrations.alembic_version AS TABLE public.alembic_version;
CREATE TABLE branchit_backup_20261109_migrations.entrevistas_ia AS TABLE public.entrevistas_ia;
CREATE TABLE branchit_backup_20261109_migrations.conteos AS
SELECT (SELECT count(*) FROM public.usuarios) AS usuarios,
       (SELECT count(*) FROM public.ofertas_empleo) AS ofertas,
       (SELECT count(*) FROM public.postulaciones) AS postulaciones,
       (SELECT count(*) FROM public.entrevistas_ia) AS entrevistas;


-- Running upgrade 0008_entrevista_diaria -> 0009_seguimiento_laboral

CREATE TABLE seguimiento_laboral (
    id SERIAL NOT NULL, 
    usuario_id INTEGER NOT NULL, 
    situacion VARCHAR(20) NOT NULL, 
    busqueda_activa BOOLEAN NOT NULL, 
    datos_cifrados TEXT NOT NULL, 
    actualizado TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id), 
    UNIQUE (usuario_id), 
    FOREIGN KEY(usuario_id) REFERENCES usuarios (id)
);

UPDATE alembic_version SET version_num='0009_seguimiento_laboral' WHERE alembic_version.version_num = '0008_entrevista_diaria';

-- Running upgrade 0009_seguimiento_laboral -> 0010_empleo_finiquito

ALTER TABLE seguimiento_laboral ADD COLUMN limite_experiencia BOOLEAN DEFAULT false NOT NULL;

UPDATE alembic_version SET version_num='0010_empleo_finiquito' WHERE alembic_version.version_num = '0009_seguimiento_laboral';

-- Running upgrade 0010_empleo_finiquito -> 0011_suscripciones

CREATE TABLE suscripciones (
    id SERIAL NOT NULL, 
    usuario_id INTEGER NOT NULL, 
    estado VARCHAR(12) NOT NULL, 
    vigente_hasta TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id), 
    CONSTRAINT ck_suscripcion_estado CHECK (estado IN ('inactiva', 'activa')), 
    UNIQUE (usuario_id), 
    FOREIGN KEY(usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE
);

UPDATE alembic_version SET version_num='0011_suscripciones' WHERE alembic_version.version_num = '0010_empleo_finiquito';

-- Running upgrade 0011_suscripciones -> 0012_entrevistas_suscripcion

ALTER TABLE entrevistas_ia ADD COLUMN creada TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL;

ALTER TABLE entrevistas_ia DROP CONSTRAINT uq_entrevista_usuario_dia;

CREATE INDEX ix_entrevistas_usuario_fecha ON entrevistas_ia (usuario_id, fecha);

UPDATE alembic_version SET version_num='0012_entrevistas_suscripcion' WHERE alembic_version.version_num = '0011_suscripciones';


DO $check$
BEGIN
    IF (SELECT version_num FROM public.alembic_version) <> '0012_entrevistas_suscripcion'
       OR (SELECT count(*) FROM public.usuarios) <> (SELECT usuarios FROM branchit_backup_20261109_migrations.conteos)
       OR (SELECT count(*) FROM public.ofertas_empleo) <> (SELECT ofertas FROM branchit_backup_20261109_migrations.conteos)
       OR (SELECT count(*) FROM public.postulaciones) <> (SELECT postulaciones FROM branchit_backup_20261109_migrations.conteos)
       OR (SELECT count(*) FROM public.entrevistas_ia) <> (SELECT entrevistas FROM branchit_backup_20261109_migrations.conteos) THEN
        RAISE EXCEPTION 'La comprobacion no coincide; se revierte la transaccion.';
    END IF;
END;
$check$;

COMMIT;

