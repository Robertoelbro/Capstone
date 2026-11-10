import sys
sys.path.insert(0,'.vercel')
from provision import api
for project in ['branchit','branchit-api']:
 data=api('/v10/projects/'+project+'/env?decrypt=true')
 values={item['key']:item.get('value','') for item in data.get('envs',[]) if 'production' in item.get('target',[])}
 print(project, sorted(values.keys()), 'expected_neon_project',values.get('NEON_PROJECT_ID')=='flat-heart-85887310')
