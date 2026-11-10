import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
from dotenv import dotenv_values
from sqlalchemy import create_engine, inspect, text

def api(endpoint, method='GET', body=None):
    args = ['npx.cmd', '--yes', 'vercel@62.4.0', 'api', endpoint,
            '--scope', 'roberto-el-bro', '--method', method]
    if body is not None:
        args += ['--input', '-']
    result = subprocess.run(args, input=json.dumps(body) if body is not None else None,
                            capture_output=True, text=True, encoding='utf-8')
    if result.returncode:
        raise RuntimeError('Vercel API failed: ' + endpoint + ' (response withheld)')
    return json.loads(result.stdout)

def database_env():
    result = api('/v10/projects/branchit/env?decrypt=true')
    values = {e['key']: e['value'] for e in result['envs'] if 'production' in e.get('target', [])}
    assert values.get('NEON_PROJECT_ID') == 'flat-heart-85887310', 'Unexpected Neon project'
    return values

def inspect_db():
    values = database_env()
    url = values.get('DATABASE_URL_UNPOOLED') or values['DATABASE_URL']
    engine = create_engine(url, connect_args={'connect_timeout': 10})
    with engine.connect() as conn:
        tables = inspect(conn).get_table_names()
        version = conn.execute(text('SELECT version_num FROM alembic_version')).scalar() if 'alembic_version' in tables else None
        print(json.dumps({'database': conn.execute(text('SELECT current_database()')).scalar(),
                          'tables': tables, 'migration': version}))
    engine.dispose()

def configure():
    local = dotenv_values(ROOT / 'backend' / '.env')
    from cryptography.fernet import Fernet
    Fernet(local['DATA_ENCRYPTION_KEY'].encode())
    assert len(local['SECRET_KEY']) >= 32
    env = {k: local[k] for k in ['SECRET_KEY', 'DATA_ENCRYPTION_KEY']}
    env['CORS_ORIGINS'] = 'https://branchit-blue.vercel.app'
    for key, value in env.items():
        result = api('/v10/projects/branchit-api/env?upsert=true', 'POST',
                     {'key': key, 'value': value, 'type': 'encrypted', 'target': ['production']})
        if result.get('error') or result.get('errors'):
            raise RuntimeError('Could not configure environment variable ' + key)
    print('Backend production variables configured; values withheld.')

def migrate():
    values = database_env()
    os.environ['DATABASE_URL'] = values['DATABASE_URL_UNPOOLED']
    os.chdir(ROOT / 'backend')
    from alembic import command
    from alembic.config import Config
    config = Config('alembic.ini')
    command.upgrade(config, 'head')
    command.current(config)

if __name__ == '__main__':
    try:
        {'inspect': inspect_db, 'configure': configure, 'migrate': migrate}[sys.argv[1]]()
    except Exception as exc:
        print('Operation failed:', type(exc).__name__, '(details withheld to protect credentials)')
        sys.exit(1)
