-- Equivalent to Alembic 0007_notificaciones -> 0008_entrevista_diaria.
DO $branchit_daily$
DECLARE current_version text;
BEGIN
    SELECT version_num INTO STRICT current_version FROM public.alembic_version FOR UPDATE;
    IF current_version = '0007_notificaciones' THEN
        CREATE TABLE public.entrevistas_ia (
            id VARCHAR(32) NOT NULL PRIMARY KEY,
            usuario_id INTEGER NOT NULL REFERENCES public.usuarios(id),
            fecha DATE NOT NULL,
            oferta_id INTEGER REFERENCES public.ofertas_empleo(id) ON DELETE SET NULL,
            datos_cifrados TEXT NOT NULL,
            turnos INTEGER NOT NULL,
            CONSTRAINT uq_entrevista_usuario_dia UNIQUE (usuario_id, fecha)
        );
        UPDATE public.alembic_version SET version_num = '0008_entrevista_diaria'
        WHERE version_num = '0007_notificaciones';
    ELSIF current_version <> '0008_entrevista_diaria' THEN
        RAISE EXCEPTION 'Version inesperada: %', current_version;
    END IF;
END $branchit_daily$;
