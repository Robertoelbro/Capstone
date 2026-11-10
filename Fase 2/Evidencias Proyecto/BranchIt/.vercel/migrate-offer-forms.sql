DO $branchit$
DECLARE current_version text;
BEGIN
  SELECT version_num INTO current_version FROM alembic_version;
  IF current_version = '0004_identidad_empresa' THEN
    ALTER TABLE ofertas_empleo
      ADD COLUMN sueldo BIGINT NULL,
      ADD COLUMN funciones TEXT NULL,
      ADD COLUMN perfiles_deseados JSON NULL,
      ADD COLUMN condiciones_laborales TEXT NULL,
      ADD COLUMN adaptada_discapacidad BOOLEAN NULL;
    UPDATE alembic_version SET version_num = '0005_ofertas_completas'
      WHERE version_num = '0004_identidad_empresa';
  ELSIF current_version <> '0005_ofertas_completas' OR current_version IS NULL THEN
    RAISE EXCEPTION 'Versión inesperada: %', current_version;
  END IF;
END $branchit$;
