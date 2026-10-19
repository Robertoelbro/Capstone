-- Equivalent to Alembic 0006_cierre_convocatorias -> 0007_notificaciones.
-- Atomic and safe to rerun; no existing application data is changed.
DO $branchit_migration$
DECLARE current_version text;
BEGIN
    SELECT version_num INTO STRICT current_version FROM public.alembic_version FOR UPDATE;
    IF current_version = '0006_cierre_convocatorias' THEN
        CREATE TABLE public.notificaciones (
            id SERIAL NOT NULL PRIMARY KEY,
            usuario_id INTEGER NOT NULL REFERENCES public.usuarios(id),
            mensaje VARCHAR(400) NOT NULL,
            destino VARCHAR(200) NOT NULL,
            leida BOOLEAN DEFAULT false NOT NULL,
            creada TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL
        );
        CREATE INDEX ix_notificaciones_usuario_id ON public.notificaciones(usuario_id);
        UPDATE public.alembic_version SET version_num = '0007_notificaciones'
        WHERE version_num = '0006_cierre_convocatorias';
    ELSIF current_version <> '0007_notificaciones' THEN
        RAISE EXCEPTION 'Version inesperada: %', current_version;
    END IF;
END $branchit_migration$;
