"""Only disposable SQLite databases and deterministic, non-production test keys."""
import base64
import contextlib
import io
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from rotate_data_encryption import RotationError, main, rotate_data, validate_destination

OLD_KEY = base64.urlsafe_b64encode(b'a' * 32).decode()
NEW_KEY = base64.urlsafe_b64encode(b'b' * 32).decode()
OLD, NEW = Fernet(OLD_KEY.encode()), Fernet(NEW_KEY.encode())
PAYLOAD = b'{"contacto":"dato-ficticio","url":"https://example.invalid/proyecto"}'


class RotationTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite://', poolclass=StaticPool)
        with self.engine.begin() as conn:
            conn.exec_driver_sql("ATTACH DATABASE ':memory:' AS branchit_backup_test")
            conn.exec_driver_sql("ATTACH DATABASE ':memory:' AS private_other")
            for prefix in ('', 'branchit_backup_test.'):
                for table in ('postulaciones', 'entrevistas_ia', 'seguimiento_laboral'):
                    conn.exec_driver_sql(f'CREATE TABLE {prefix}{table} (id INTEGER, datos_cifrados TEXT, etiqueta TEXT)')
                    conn.execute(text(f'INSERT INTO {prefix}{table} VALUES (1, :token, :label)'),
                                 {'token': OLD.encrypt(PAYLOAD).decode(), 'label': 'sin modificar'})
            conn.exec_driver_sql('CREATE TABLE private_other.postulaciones (id INTEGER, datos_cifrados TEXT)')
            conn.exec_driver_sql("INSERT INTO private_other.postulaciones VALUES (1, 'NO-TOCAR')")
            conn.exec_driver_sql('CREATE TABLE archivos_portfolio (id INTEGER, datos_cifrados TEXT)')
            conn.exec_driver_sql("INSERT INTO archivos_portfolio VALUES (1, 'NO-TOCAR')")

    def tearDown(self):
        self.engine.dispose()

    def tokens(self):
        with self.engine.connect() as conn:
            return {(prefix + table): conn.exec_driver_sql(f'SELECT id, datos_cifrados, etiqueta FROM {prefix}{table}').all()
                    for prefix in ('', 'branchit_backup_test.')
                    for table in ('postulaciones', 'entrevistas_ia', 'seguimiento_laboral')}

    def test_default_dry_run_validates_all_whitelisted_schemas_without_modifications(self):
        before = self.tokens()
        result = rotate_data(self.engine, OLD_KEY, NEW_KEY)
        self.assertEqual(self.tokens(), before)
        self.assertEqual(len(result), 6)
        self.assertEqual(sum(item['validadas'] for item in result), 6)
        self.assertEqual(sum(item['recifradas'] for item in result), 0)
        self.assertNotIn('private_other', str(result))
        self.assertNotIn('archivos_portfolio', str(result))

    def test_payment_tokens_are_rotated_alongside_existing_private_data(self):
        token = OLD.encrypt(b'{"token":"integration-only-token"}').decode()
        with self.engine.begin() as conn:
            conn.exec_driver_sql('CREATE TABLE pagos_webpay (id TEXT PRIMARY KEY, datos_cifrados TEXT)')
            conn.execute(text('INSERT INTO pagos_webpay VALUES (:id, :token)'), {'id':'test-order','token':token})
        report = rotate_data(self.engine, OLD_KEY, NEW_KEY, apply=True)
        payments = next(item for item in report if item['tabla'] == 'main.pagos_webpay')
        self.assertEqual(payments['recifradas'], 1)
        with self.engine.connect() as conn:
            saved = conn.exec_driver_sql('SELECT datos_cifrados FROM pagos_webpay').scalar_one()
        self.assertEqual(NEW.decrypt(saved.encode()), b'{"token":"integration-only-token"}')
        with self.assertRaises(InvalidToken):
            OLD.decrypt(saved.encode())

    def test_apply_rotates_public_and_backups_preserving_ids_plaintext_and_other_columns(self):
        before = self.tokens()
        result = rotate_data(self.engine, OLD_KEY, NEW_KEY, apply=True)
        self.assertEqual(sum(item['recifradas'] for item in result), 6)
        after = self.tokens()
        for table, rows in after.items():
            self.assertEqual(rows[0].id, before[table][0].id)
            self.assertEqual(rows[0].etiqueta, before[table][0].etiqueta)
            self.assertNotEqual(rows[0].datos_cifrados, before[table][0].datos_cifrados)
            self.assertEqual(NEW.decrypt(rows[0].datos_cifrados.encode()), PAYLOAD)
            with self.assertRaises(InvalidToken):
                OLD.decrypt(rows[0].datos_cifrados.encode())
        with self.engine.connect() as conn:
            self.assertEqual(conn.exec_driver_sql('SELECT datos_cifrados FROM private_other.postulaciones').scalar(), 'NO-TOCAR')

    def test_invalid_ciphertext_in_last_backup_aborts_before_any_updates(self):
        with self.engine.begin() as conn:
            conn.exec_driver_sql("UPDATE branchit_backup_test.seguimiento_laboral SET datos_cifrados='dato-sensible-invalido'")
        before = self.tokens()
        with self.assertRaises(RotationError) as failure:
            rotate_data(self.engine, OLD_KEY, NEW_KEY, apply=True)
        self.assertEqual(self.tokens(), before)
        self.assertNotIn('dato-sensible-invalido', str(failure.exception))
        self.assertNotIn(OLD_KEY, str(failure.exception))

    def test_multiple_batches_rotate_every_row_and_leave_null_ciphertexts_unchanged(self):
        with self.engine.begin() as conn:
            conn.execute(text('INSERT INTO postulaciones VALUES (:id, :token, :label)'),
                [{'id': i, 'token': OLD.encrypt(PAYLOAD).decode(), 'label': 'sin modificar'} for i in range(2, 207)])
            conn.exec_driver_sql("INSERT INTO postulaciones VALUES (207, NULL, 'sin modificar')")
        result = rotate_data(self.engine, OLD_KEY, NEW_KEY, apply=True)
        public = next(row for row in result if row['tabla'] == 'main.postulaciones')
        self.assertEqual(public['recifradas'], 206)
        with self.engine.connect() as conn:
            rows = conn.exec_driver_sql('SELECT datos_cifrados FROM postulaciones ORDER BY id').scalars().all()
        self.assertEqual(len(rows), 207)
        self.assertIsNone(rows[-1])
        for value in rows[:-1]:
            self.assertEqual(NEW.decrypt(value.encode()), PAYLOAD)

    def test_write_error_after_first_table_rolls_back_every_updated_table(self):
        with self.engine.begin() as conn:
            conn.exec_driver_sql("CREATE TRIGGER reject_update BEFORE UPDATE ON postulaciones BEGIN SELECT RAISE(ABORT, 'hidden-sensitive-driver-error'); END")
        before = self.tokens()
        with self.assertRaises(RotationError) as failure:
            rotate_data(self.engine, OLD_KEY, NEW_KEY, apply=True)
        self.assertEqual(self.tokens(), before)
        self.assertNotIn('hidden-sensitive-driver-error', str(failure.exception))
        self.assertNotIn('UPDATE', str(failure.exception))

    def test_silent_trigger_skip_is_detected_before_commit_and_rolls_back_other_tables(self):
        with self.engine.begin() as conn:
            conn.exec_driver_sql('CREATE TRIGGER skip_update BEFORE UPDATE ON postulaciones BEGIN SELECT RAISE(IGNORE); END')
        before = self.tokens()
        with self.assertRaises(RotationError):
            rotate_data(self.engine, OLD_KEY, NEW_KEY, apply=True)
        self.assertEqual(self.tokens(), before)

    def test_duplicate_identifiers_in_backup_and_invalid_keys_are_rejected(self):
        with self.engine.begin() as conn:
            conn.execute(text('INSERT INTO branchit_backup_test.postulaciones VALUES (1, :token, :label)'),
                         {'token': OLD.encrypt(PAYLOAD).decode(), 'label': 'duplicado'})
        before = self.tokens()
        for current, new in ((OLD_KEY, NEW_KEY), ('incorrecta', NEW_KEY), (OLD_KEY, OLD_KEY)):
            with self.assertRaises(RotationError):
                rotate_data(self.engine, current, new, apply=True)
        self.assertEqual(self.tokens(), before)

    def test_destination_requires_neon_expected_database_or_explicit_local_sqlite(self):
        accepted = validate_destination('postgresql://dummy:dummy@ep-demo.neon.tech/neondb', 'neondb')
        self.assertEqual(accepted.database, 'neondb')
        self.assertEqual(validate_destination('sqlite://', None, True).get_backend_name(), 'sqlite')
        for url, expected, local in (
            ('sqlite://', None, False),
            ('postgresql://dummy:dummy@ep-demo.neon.tech/neondb', None, False),
            ('postgresql://dummy:dummy@ep-demo.neon.tech/otra', 'neondb', False),
            ('postgresql://dummy:dummy@neon.tech.attacker.invalid/neondb', 'neondb', False),
            ('postgresql://dummy:dummy@localhost/neondb', 'neondb', True)):
            with self.assertRaises(RotationError) as failure:
                validate_destination(url, expected, local)
            self.assertNotIn('dummy', str(failure.exception))
            self.assertNotIn(url, str(failure.exception))

    def test_cli_only_outputs_counts_and_handles_missing_env_without_secrets(self):
        output, errors = io.StringIO(), io.StringIO()
        env = {'DATABASE_URL': 'sqlite://', 'DATA_ENCRYPTION_KEY': OLD_KEY,
               'BRANCHIT_NEW_ENCRYPTION_KEY': NEW_KEY}
        # Keep the already prepared disposable engine; main disposes it afterwards.
        with patch.dict(os.environ, env), patch('rotate_data_encryption.create_engine', return_value=self.engine), \
                contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            self.assertEqual(main(['--allow-local']), 0)
        result = output.getvalue() + errors.getvalue()
        self.assertIn('sin cambios', result)
        self.assertNotIn(OLD_KEY, result)
        self.assertNotIn(NEW_KEY, result)
        self.assertNotIn('dato-ficticio', result)
        self.assertNotIn('example.invalid', result)
