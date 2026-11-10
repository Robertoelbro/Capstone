from pathlib import Path
import sys,httpx
sys.path.insert(0,str(Path('backend').resolve()))
from scripts.seed_jobs import company_accounts
with httpx.Client(base_url='https://branchit-api.vercel.app',timeout=45) as client:
 for a in company_accounts():
  r=client.post('/auth/login',json={'email':a['correo'],'password':a['contraseña']})
  assert r.status_code==200, f"Login {a['correo']}: HTTP {r.status_code}"
  data=r.json()
  result=client.get(f"/empresas/{data['user']['id']}/resumen",headers={'Authorization':'Bearer '+data['access_token']})
  assert result.status_code==200, f'Summary: HTTP {result.status_code}'
  assert result.json()['ofertas']==10, result.json()['ofertas']
  print(a['correo'], 'login OK; 10 ofertas', flush=True)
