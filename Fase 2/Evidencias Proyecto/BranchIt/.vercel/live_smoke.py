import json, secrets, time
from pathlib import Path
import httpx

root = Path(__file__).parent
state = {'password': secrets.token_urlsafe(20), 'suffix': str(int(time.time()))}
(root / 'demo-credentials.json').write_text(json.dumps(state), encoding='utf-8')
c = httpx.Client(base_url='https://branchit-api.vercel.app', timeout=60)
def req(method, path, status=200, token=None, **kwargs):
    r = c.request(method, path, headers={'Authorization': 'Bearer '+token} if token else {}, **kwargs)
    assert r.status_code == status, f'{method} {path}: expected {status}, got {r.status_code}'
    print(f'PASS {method} {path}: {status}', flush=True)
    return r.json() if r.content else None

req('GET', '/api/employment/jobs')
r=c.options('/auth/login',headers={'Origin':'https://branchit-blue.vercel.app','Access-Control-Request-Method':'POST','Access-Control-Request-Headers':'content-type'})
assert r.status_code==200 and r.headers.get('access-control-allow-origin')=='https://branchit-blue.vercel.app'
print('PASS frontend CORS',flush=True)
for role in ['empresa','egresado']:
    email=f'branchit.demo.{role}.{state["suffix"]}@example.com'
    payload={'email':email,'password':state['password']}
    payload.update({'nombre_empresa':'DEMO - Empresa academica','rubro':'Pruebas educativas'} if role=='empresa' else {'nombre':'Demo','apellido':'Egresado','carrera':'Informatica'})
    user=req('POST','/auth/registro/'+role,201,json=payload)
    state[role]={'email':email,'id':user['id']}
    (root/'demo-credentials.json').write_text(json.dumps(state,indent=2),encoding='utf-8')
    login=req('POST','/auth/login',json={'email':email,'password':state['password']})
    state[role]['token']=login['access_token']
e,g=state['empresa'],state['egresado']
req('GET','/auth/me',token=g['token'])
req('POST',f'/egresados/{g["id"]}/presentacion',201,token=g['token'],json={'presentacion':'Perfil ficticio para demostrar BranchIT ante el docente.'})
offer=req('POST',f'/empresas/{e["id"]}/ofertas',201,token=e['token'],json={'titulo':'DEMO - Practica de desarrollo web','descripcion':'Oferta ficticia para demostracion academica. No corresponde a una vacante real.','modalidad':'Remoto','preguntas':[{'id':'motivo','etiqueta':'Que puedes aportar?','tipo':'parrafo','obligatoria':True}]})
oid=offer['id']
payload={'oferta_id':oid,'formulario_version':offer['formulario_version'],'mensaje':'Postulacion ficticia de demostracion.','respuestas':{'motivo':'Desarrollo de aplicaciones web y trabajo en equipo.'},'consentimiento':True}
req('POST','/api/employment/applications',201,token=g['token'],json=payload)
req('POST','/api/employment/applications',409,token=g['token'],json=payload)
req('POST','/api/employment/applications',403,token=e['token'],json=payload)
applications=req('GET',f'/api/employment/jobs/{oid}/applications',token=e['token'])
assert applications[0]['datos']['respuestas']==payload['respuestas']
print('PASS encrypted application round trip',flush=True)
req('GET','/api/employment/applications/me',token=g['token'])
req('GET',f'/api/employment/jobs/{oid}/applications',403,token=g['token'])
req('GET','/auth/me',401)
req('GET',f'/empresas/{e["id"]}/resumen',token=e['token'])
for user in [g,e]:
    req('POST','/auth/logout',204,token=user['token'])
    req('GET','/auth/me',401,token=user['token'])
    del user['token']
state['offer_id']=oid
(root/'demo-credentials.json').write_text(json.dumps(state,indent=2),encoding='utf-8')
print('SUCCESS: both roles and Neon persistence verified; demo credentials saved privately.')
