-- Estructura generada desde modelos; referencia documental, no ejecutar sobre la BD existente.
CREATE TYPE tipousuario AS ENUM ('egresado', 'empresa');


CREATE TABLE usuarios (
	id SERIAL NOT NULL, 
	rut VARCHAR(12), 
	telefono VARCHAR(30), 
	fecha_identidad DATE, 
	email VARCHAR(255) NOT NULL, 
	password_hash VARCHAR(255) NOT NULL, 
	tipo tipousuario NOT NULL, 
	fecha_registro TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	activo BOOLEAN NOT NULL, 
	token_version INTEGER NOT NULL, 
	PRIMARY KEY (id)
)

;


CREATE TABLE archivos_portfolio (
	id VARCHAR(32) NOT NULL, 
	usuario_id INTEGER NOT NULL, 
	tipo VARCHAR(20) NOT NULL, 
	nombre VARCHAR(180) NOT NULL, 
	mime VARCHAR(80) NOT NULL, 
	tamano INTEGER NOT NULL, 
	duracion INTEGER, 
	pathname VARCHAR(255) NOT NULL, 
	verificado BOOLEAN NOT NULL, 
	creado TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(usuario_id) REFERENCES usuarios (id), 
	UNIQUE (pathname)
)

;


CREATE TABLE notificaciones (
	id SERIAL NOT NULL, 
	usuario_id INTEGER NOT NULL, 
	mensaje VARCHAR(400) NOT NULL, 
	destino VARCHAR(200) NOT NULL, 
	leida BOOLEAN NOT NULL, 
	creada TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(usuario_id) REFERENCES usuarios (id)
)

;


CREATE TABLE perfiles_egresado (
	id SERIAL NOT NULL, 
	usuario_id INTEGER NOT NULL, 
	nombre VARCHAR(100) NOT NULL, 
	apellido VARCHAR(100) NOT NULL, 
	carrera VARCHAR(150), 
	anio_egreso INTEGER, 
	presentacion TEXT, 
	linkedin_url VARCHAR(255), 
	foto_url VARCHAR(255), 
	portfolio JSON NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (usuario_id), 
	FOREIGN KEY(usuario_id) REFERENCES usuarios (id)
)

;


CREATE TABLE perfiles_empresa (
	id SERIAL NOT NULL, 
	usuario_id INTEGER NOT NULL, 
	nombre_empresa VARCHAR(150) NOT NULL, 
	rubro VARCHAR(150), 
	descripcion TEXT, 
	sitio_web VARCHAR(255), 
	logo_url VARCHAR(255), 
	foto_id VARCHAR(32), 
	PRIMARY KEY (id), 
	UNIQUE (usuario_id), 
	FOREIGN KEY(usuario_id) REFERENCES usuarios (id), 
	FOREIGN KEY(foto_id) REFERENCES archivos_portfolio (id)
)

;


CREATE TABLE ofertas_empleo (
	id SERIAL NOT NULL, 
	empresa_id INTEGER NOT NULL, 
	titulo VARCHAR(150) NOT NULL, 
	descripcion TEXT NOT NULL, 
	requisitos TEXT, 
	ubicacion VARCHAR(150), 
	modalidad VARCHAR(50), 
	fecha_publicacion TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	activa BOOLEAN NOT NULL, 
	preguntas JSON NOT NULL, 
	formulario_version INTEGER NOT NULL, 
	categoria VARCHAR(80) NOT NULL, 
	demo_clave VARCHAR(80), 
	sueldo BIGINT, 
	funciones TEXT, 
	perfiles_deseados JSON, 
	condiciones_laborales TEXT, 
	adaptada_discapacidad BOOLEAN, 
	PRIMARY KEY (id), 
	FOREIGN KEY(empresa_id) REFERENCES perfiles_empresa (id)
)

;


CREATE TABLE entrevistas_ia (
	id VARCHAR(32) NOT NULL, 
	usuario_id INTEGER NOT NULL, 
	fecha DATE NOT NULL, 
	oferta_id INTEGER, 
	datos_cifrados TEXT NOT NULL, 
	turnos INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_entrevista_usuario_dia UNIQUE (usuario_id, fecha), 
	FOREIGN KEY(usuario_id) REFERENCES usuarios (id), 
	FOREIGN KEY(oferta_id) REFERENCES ofertas_empleo (id) ON DELETE SET NULL
)

;


CREATE TABLE postulaciones (
	id SERIAL NOT NULL, 
	oferta_id INTEGER NOT NULL, 
	egresado_id INTEGER NOT NULL, 
	fecha_postulacion TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	datos_cifrados TEXT NOT NULL, 
	seleccionada BOOLEAN NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_postulacion_oferta_egresado UNIQUE (oferta_id, egresado_id), 
	FOREIGN KEY(oferta_id) REFERENCES ofertas_empleo (id), 
	FOREIGN KEY(egresado_id) REFERENCES perfiles_egresado (id)
)

;

CREATE UNIQUE INDEX ix_usuarios_email ON usuarios (email);

CREATE INDEX ix_usuarios_id ON usuarios (id);

CREATE UNIQUE INDEX uq_usuarios_rut ON usuarios (rut);

CREATE INDEX ix_archivos_portfolio_usuario_id ON archivos_portfolio (usuario_id);

CREATE INDEX ix_notificaciones_usuario_id ON notificaciones (usuario_id);

CREATE INDEX ix_perfiles_egresado_id ON perfiles_egresado (id);

CREATE INDEX ix_perfiles_empresa_id ON perfiles_empresa (id);

CREATE INDEX ix_ofertas_empleo_id ON ofertas_empleo (id);

CREATE UNIQUE INDEX uq_ofertas_demo_clave ON ofertas_empleo (demo_clave);

CREATE INDEX ix_postulaciones_egresado_id ON postulaciones (egresado_id);

CREATE INDEX ix_postulaciones_oferta_id ON postulaciones (oferta_id);

CREATE UNIQUE INDEX uq_seleccion_por_oferta ON postulaciones (oferta_id) WHERE seleccionada = true;
