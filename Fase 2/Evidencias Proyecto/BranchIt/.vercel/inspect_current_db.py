import sys,json
sys.path.insert(0,'.vercel')
from provision import api
from urllib.parse import urlsplit
from sqlalchemy import create_engine,text,inspect
values={item['key']:item.get('value','') for item in api('/v10/projects/branchit-api/env?decrypt=true').get('envs',[]) if 'production' in item.get('target',[])}
print('Neon project:',repr(values.get('NEON_PROJECT_ID')))
url=values.get('DATABASE_URL_UNPOOLED') or values['DATABASE_URL']
print('Neon host verified:',(urlsplit(url).hostname or '').endswith('.neon.tech'))
assert (urlsplit(url).hostname or '').endswith('.neon.tech')
engine=create_engine(url,connect_args={'connect_timeout':10})
with engine.connect() as conn:
 print(json.dumps({'migration':conn.execute(text('SELECT version_num FROM alembic_version')).scalar(),'users':conn.execute(text('SELECT COUNT(*) FROM usuarios')).scalar(),'jobs':conn.execute(text('SELECT COUNT(*) FROM ofertas_empleo')).scalar(),'columns':[col['name'] for col in inspect(conn).get_columns('ofertas_empleo')]}))
engine.dispose()
