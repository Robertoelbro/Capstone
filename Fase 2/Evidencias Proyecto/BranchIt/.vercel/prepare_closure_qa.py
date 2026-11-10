import httpx
base='http://127.0.0.1:8003'
with httpx.Client(base_url=base) as client:
 login=client.post('/auth/login',json={'email':'egresado@example.com','password':'EgresadoDemo2026!'})
 assert login.status_code==200
 headers={'Authorization':'Bearer '+login.json()['access_token']}
 job=client.get('/api/employment/jobs/1').json()
 answers={q['id']:q['opciones'][0] if q['tipo']=='seleccion' else [q['opciones'][0]] if q['tipo']=='seleccion_multiple' else '7' if q['tipo']=='numero' else 'Un proyecto académico con React.' for q in job['preguntas']}
 response=client.post('/api/employment/applications',headers=headers,json={'oferta_id':1,'formulario_version':job['formulario_version'],'consentimiento':True,'respuestas':answers})
 print('Postulación ficticia local:',response.status_code)
 assert response.status_code in (201,409)
