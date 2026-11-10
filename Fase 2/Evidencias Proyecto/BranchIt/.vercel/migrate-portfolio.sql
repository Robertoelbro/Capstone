DO $branchit$ BEGIN
IF (SELECT version_num FROM alembic_version) <> '0002_postulaciones' THEN RAISE EXCEPTION 'Unexpected migration version'; END IF;


-- Running upgrade 0002_postulaciones -> 0003_portfolio

ALTER TABLE perfiles_egresado ADD COLUMN portfolio JSON DEFAULT '{}' NOT NULL;

ALTER TABLE ofertas_empleo ADD COLUMN categoria VARCHAR(80) DEFAULT 'General' NOT NULL;

ALTER TABLE ofertas_empleo ADD COLUMN demo_clave VARCHAR(80);

CREATE UNIQUE INDEX uq_ofertas_demo_clave ON ofertas_empleo (demo_clave);

CREATE TABLE archivos_portfolio (
    id VARCHAR(32) NOT NULL, 
    usuario_id INTEGER NOT NULL, 
    tipo VARCHAR(20) NOT NULL, 
    nombre VARCHAR(180) NOT NULL, 
    mime VARCHAR(80) NOT NULL, 
    tamano INTEGER NOT NULL, 
    duracion INTEGER, 
    pathname VARCHAR(255) NOT NULL, 
    verificado BOOLEAN DEFAULT false NOT NULL, 
    creado TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(usuario_id) REFERENCES usuarios (id), 
    UNIQUE (pathname)
);

CREATE INDEX ix_archivos_portfolio_usuario_id ON archivos_portfolio (usuario_id);

UPDATE alembic_version SET version_num='0003_portfolio' WHERE alembic_version.version_num = '0002_postulaciones';




END $branchit$;