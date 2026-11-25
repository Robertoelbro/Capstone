"""Rotate Fernet data keys atomically. Reads credentials only from environment.

Default is validation only. Stop application writes before a production rotation
and coordinate the new DATA_ENCRYPTION_KEY with the API before resuming traffic.
No plaintext, connection URLs, keys, record identifiers or SQL errors are printed.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass

from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine, make_url

TABLES = frozenset({'postulaciones', 'entrevistas_ia', 'seguimiento_laboral', 'pagos_webpay'})
BACKUP_SCHEMA = re.compile(r'^branchit_backup_[A-Za-z0-9_]+$')
BATCH_SIZE = 100


class RotationError(Exception):
    """An intentionally sanitized failure: safe to show without SQL parameters."""


@dataclass(frozen=True)
class Target:
    schema: str | None
    table: str

    @property
    def label(self):
        return f'{self.schema or "main"}.{self.table}'


def validate_destination(database_url: str, expected_db: str | None, allow_local=False):
    """Refuse unreviewed destinations; allow_local supports isolated SQLite only."""
    try:
        url = make_url(database_url)
        if url.get_backend_name() == 'sqlite' and allow_local:
            return url
        if (url.get_backend_name() != 'postgresql' or expected_db != 'neondb'
                or url.database != expected_db or not url.host
                or not url.host.lower().endswith('.neon.tech')):
            raise RotationError('Destino rechazado: requiere PostgreSQL Neon y --expected-db neondb, o SQLite con --allow-local.')
        return url
    except RotationError:
        raise
    except Exception:
        raise RotationError('DATABASE_URL no tiene un formato admitido.') from None


def qualified(conn, target):
    quote = conn.dialect.identifier_preparer.quote
    return f'{quote(target.schema)}.{quote(target.table)}' if target.schema else quote(target.table)


def discover_targets(conn):
    inspector = inspect(conn)
    dialect = conn.dialect.name
    if dialect not in ('postgresql', 'sqlite'):
        raise RotationError('Motor no admitido para esta rotación.')
    schemas = inspector.get_schema_names()
    allowed = ([None] if dialect == 'sqlite' else ['public'])
    allowed += [s for s in schemas if BACKUP_SCHEMA.fullmatch(s)]
    targets = []
    for schema in allowed:
        for table in sorted(set(inspector.get_table_names(schema=schema)) & TABLES):
            columns = {c['name'] for c in inspector.get_columns(table, schema=schema)}
            if 'datos_cifrados' not in columns:
                continue
            if 'id' not in columns:
                raise RotationError('Una tabla cifrada no tiene la columna id necesaria para una rotación segura.')
            targets.append(Target(schema, table))
    targets.sort(key=lambda t: (t.schema or '', t.table))
    if not targets:
        raise RotationError('No se encontraron las tablas cifradas esperadas; no se realizará ningún cambio.')
    return targets


def _token(value):
    if isinstance(value, str):
        return value.encode('ascii')
    if isinstance(value, bytes):
        return value
    raise RotationError('Una fila contiene un valor cifrado con formato no admitido.')


def _validate_rows(conn, target, old_cipher):
    table = qualified(conn, target)
    # Backups created with CREATE TABLE AS may have no declared primary key.
    # Explicit uniqueness checks keep updates safe even for those tables.
    duplicate = conn.execute(text(
        f'SELECT id FROM {table} GROUP BY id HAVING COUNT(*) > 1 LIMIT 1')).first()
    null_id = conn.execute(text(f'SELECT id FROM {table} WHERE id IS NULL LIMIT 1')).first()
    if duplicate is not None or null_id is not None:
        raise RotationError('Una tabla tiene identificadores duplicados o nulos; no se realizará ningún cambio.')
    rows = conn.execute(text(f'SELECT datos_cifrados FROM {table} WHERE datos_cifrados IS NOT NULL'))
    count = 0
    while batch := rows.fetchmany(BATCH_SIZE):
        for (encrypted,) in batch:
            try:
                old_cipher.decrypt(_token(encrypted))
            except (InvalidToken, ValueError, UnicodeError):
                raise RotationError('Hay datos que no se descifran con la clave actual; la rotación se canceló sin cambios.') from None
            count += 1
    return count


def _rewrite_rows(conn, target, old_cipher, new_cipher):
    table = qualified(conn, target)
    rows = conn.execute(text(f'SELECT id, datos_cifrados FROM {table} WHERE datos_cifrados IS NOT NULL ORDER BY id'))
    count = 0
    while batch := rows.fetchmany(BATCH_SIZE):
        updates = []
        for row_id, encrypted in batch:
            # Plaintext exists only transiently in memory, never as a file or log.
            replacement = new_cipher.encrypt(old_cipher.decrypt(_token(encrypted))).decode('ascii')
            updates.append({'row_id': row_id, 'replacement': replacement})
        conn.execute(text(f'UPDATE {table} SET datos_cifrados = :replacement WHERE id = :row_id'), updates)
        count += len(updates)
    return count


def rotate_data(engine: Engine, current_key: str, new_key: str, *, apply=False):
    """Validate every ciphertext first, then rewrite all tables in one transaction.

    The caller validates the engine destination. This core also supports isolated
    SQLite tests. The return value contains only whitelisted table names/counts.
    """
    try:
        if not current_key or not new_key or current_key == new_key:
            raise RotationError('Configura dos claves Fernet válidas y distintas en las variables privadas.')
        old_cipher, new_cipher = Fernet(current_key.encode('ascii')), Fernet(new_key.encode('ascii'))
    except RotationError:
        raise
    except (ValueError, UnicodeError, TypeError):
        raise RotationError('Una clave Fernet no es válida. Revisa las variables privadas.') from None
    try:
        with engine.begin() as conn:
            if conn.dialect.name == 'sqlite':
                conn.exec_driver_sql('BEGIN IMMEDIATE')
            targets = discover_targets(conn)
            if conn.dialect.name == 'postgresql':
                for target in targets:
                    conn.exec_driver_sql(f'LOCK TABLE {qualified(conn, target)} IN SHARE ROW EXCLUSIVE MODE')
            counts = [(target, _validate_rows(conn, target, old_cipher)) for target in targets]
            if apply:
                for target, validated in counts:
                    changed = _rewrite_rows(conn, target, old_cipher, new_cipher)
                    if changed != validated:
                        raise RotationError('Cambió la cantidad de filas durante la rotación; se revirtieron los cambios.')
                # Detect silent trigger skips or unexpected ciphertext mutations
                # before commit, rather than trusting executemany row counts.
                for target, validated in counts:
                    if _validate_rows(conn, target, new_cipher) != validated:
                        raise RotationError('La verificación final no coincide; se revirtieron los cambios.')
            return [{'tabla': target.label, 'validadas': count, 'recifradas': count if apply else 0}
                    for target, count in counts]
    except RotationError:
        raise
    except Exception:
        # Suppress driver error strings: they may contain SQL parameters and URLs.
        raise RotationError('La operación de datos falló. La transacción se revirtió; no se publican detalles sensibles.') from None


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--apply', action='store_true', help='Recifrar en una única transacción; requiere coordinación de la clave del servidor.')
    mode.add_argument('--dry-run', action='store_true', help='Solo validar (opción predeterminada).')
    parser.add_argument('--expected-db', choices=['neondb'], help='Confirmación explícita del nombre de la base Neon.')
    parser.add_argument('--allow-local', action='store_true', help='Permitir únicamente SQLite local para pruebas aisladas.')
    args = parser.parse_args(argv)
    engine = None
    try:
        url = validate_destination(os.environ.get('DATABASE_URL', ''), args.expected_db, args.allow_local)
        engine = create_engine(url, pool_pre_ping=True, hide_parameters=True)
        report = rotate_data(engine, os.environ.get('DATA_ENCRYPTION_KEY', ''),
                             os.environ.get('BRANCHIT_NEW_ENCRYPTION_KEY', ''), apply=args.apply)
        print('Modo: aplicación' if args.apply else 'Modo: validación, sin cambios')
        for item in report:
            print(f"{item['tabla']}: validadas={item['validadas']}, recifradas={item['recifradas']}")
        return 0
    except RotationError as error:
        print(str(error), file=sys.stderr)
        return 1
    except Exception:
        print('No fue posible preparar la rotación. Revisa la configuración privada del entorno.', file=sys.stderr)
        return 1
    finally:
        if engine is not None:
            engine.dispose()


if __name__ == '__main__':
    raise SystemExit(main())
