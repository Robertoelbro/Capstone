import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from alembic import command
from alembic.config import Config
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import create_engine, text, inspect
import test_flows  # Establish isolated test configuration before app imports.
from app import config
from app.database import Base


class MigrationTests(unittest.TestCase):
    def test_upgrade_preserves_existing_data_and_downgrade(self):
        with tempfile.TemporaryDirectory() as directory:
            url = 'sqlite:///' + str(Path(directory) / 'migration.db').replace('\\', '/')
            with patch.object(config, 'DATABASE_URL', url):
                cfg = Config('alembic.ini')
                command.upgrade(cfg, '0001_esquema_inicial')
                engine = create_engine(url)
                with engine.begin() as connection:
                    connection.execute(text("INSERT INTO usuarios (id,email,password_hash,tipo,fecha_registro,activo) VALUES (1,'migration@example.com','hash','empresa','2026-10-04',1)"))
                    connection.execute(text("INSERT INTO perfiles_empresa (id,usuario_id,nombre_empresa) VALUES (1,1,'Empresa existente')"))
                    connection.execute(text("INSERT INTO ofertas_empleo (id,empresa_id,titulo,descripcion,fecha_publicacion,activa) VALUES (1,1,'Oferta existente','Descripción','2026-10-04',1)"))
                command.upgrade(cfg, 'head')
                with engine.connect() as connection:
                    self.assertEqual(connection.execute(text('SELECT token_version FROM usuarios')).scalar(), 0)
                    self.assertEqual(connection.execute(text('SELECT formulario_version FROM ofertas_empleo')).scalar(), 1)
                    self.assertEqual(connection.execute(text('SELECT titulo FROM ofertas_empleo')).scalar(), 'Oferta existente')
                    differences = compare_metadata(MigrationContext.configure(connection), Base.metadata)
                    self.assertEqual(differences, [])
                command.downgrade(cfg, '0001_esquema_inicial')
                self.assertNotIn('postulaciones', inspect(engine).get_table_names())
                with engine.connect() as connection:
                    self.assertEqual(connection.execute(text('SELECT count(*) FROM usuarios')).scalar(), 1)
                engine.dispose()

    def test_postgresql_offline_sql(self):
        with patch.object(config, 'DATABASE_URL', 'postgresql+psycopg2://test:test@localhost/test'):
            output = io.StringIO()
            command.upgrade(Config('alembic.ini', output_buffer=output), 'head', sql=True)
            sql = output.getvalue()
            self.assertEqual(sql.count('CREATE TYPE tipousuario'), 1)
            self.assertIn('CREATE TABLE postulaciones', sql)
            self.assertIn('uq_postulacion_oferta_egresado', sql)
            self.assertIn('ADD COLUMN preguntas JSON', sql)
