DO $migration$ BEGIN
IF (SELECT version_num FROM alembic_version) IS DISTINCT FROM '0003_portfolio' THEN RAISE EXCEPTION 'Unexpected migration version'; END IF;


-- Running upgrade 0003_portfolio -> 0004_identidad_empresa

ALTER TABLE usuarios ADD COLUMN rut VARCHAR(12);

ALTER TABLE usuarios ADD COLUMN telefono VARCHAR(30);

ALTER TABLE usuarios ADD COLUMN fecha_identidad DATE;

CREATE UNIQUE INDEX uq_usuarios_rut ON usuarios (rut);

ALTER TABLE perfiles_empresa ADD COLUMN foto_id VARCHAR(32);

ALTER TABLE perfiles_empresa ADD CONSTRAINT fk_empresa_foto FOREIGN KEY(foto_id) REFERENCES archivos_portfolio (id);

UPDATE alembic_version SET version_num='0004_identidad_empresa' WHERE alembic_version.version_num = '0003_portfolio';




END $migration$;