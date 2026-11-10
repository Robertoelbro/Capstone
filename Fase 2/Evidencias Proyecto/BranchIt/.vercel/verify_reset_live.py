import json,sys
from pathlib import Path
import httpx
sys.path.insert(0,str(Path('backend').resolve()))
from scripts.seed_jobs import company_accounts
with httpx.Client(base_url='https://branchit-api.vercel.app',timeout=30) as client:
 verified=0
 for account in company_accounts():
  login=client.post('/auth/login',json={'email':account['correo'],'password':account['contraseña']})
  if login.status_code != 200:
   print(json.dumps({'verified':verified,'failed_account_index':verified,'login_status':login.status_code}));sys.exit(1)
  session=login.json()
  headers={'Authorization':'Bearer '+session['access_token']}
  result=client.get(f"/empresas/{session['user']['id']}/ofertas",headers=headers)
  assert result.status_code==200, 'Offer listing failed'
  jobs=result.json()
  assert len(jobs)==10 and all(j['activa'] and j['sueldo']>0 and j['funciones'] and j['perfiles_deseados'] and j['condiciones_laborales'] and j['adaptada_discapacidad'] is not None for j in jobs)
  verified+=1
 public=client.get('/api/employment/jobs')
 assert public.status_code==200 and len(public.json())==100
 print(json.dumps({'empresas_con_login_correcto':verified,'ofertas_por_empresa':10,'ofertas_publicas_completas':100}))
