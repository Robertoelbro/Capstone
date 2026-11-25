-- Alternativa a Alembic para una base que esté EXACTAMENTE en 0008.
-- Respaldar y comprobar el proyecto/rama/base antes de ejecutar.
-- No ejecutar si ya se aplicó alembic upgrade head. No contiene datos personales.
BEGIN;
DO $migration$
BEGIN
    IF (SELECT count(*) FROM alembic_version) <> 1 OR NOT EXISTS (
        SELECT 1 FROM alembic_version WHERE version_num = '0008_entrevista_diaria'
    ) THEN
        RAISE EXCEPTION 'Se requiere 0008_entrevista_diaria. Revise alembic current.';
    END IF;
END;
$migration$;

CREATE TABLE seguimiento_laboral (
    id SERIAL NOT NULL,
    usuario_id INTEGER NOT NULL,
    situacion VARCHAR(20) NOT NULL,
    busqueda_activa BOOLEAN NOT NULL,
    datos_cifrados TEXT NOT NULL,
    actualizado TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (usuario_id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

UPDATE alembic_version
SET version_num = '0009_seguimiento_laboral'
WHERE version_num = '0008_entrevista_diaria';
COMMIT;
