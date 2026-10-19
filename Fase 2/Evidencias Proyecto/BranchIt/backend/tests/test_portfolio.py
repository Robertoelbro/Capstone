import unittest
from unittest.mock import patch
import test_flows as flows
from app.models import ArchivoPortfolio, OfertaEmpleo
from scripts.seed_jobs import seed, jobs, company_accounts

class PortfolioFlows(unittest.TestCase):
    setUp=flows.AccountFlows.setUp
    tearDown=flows.AccountFlows.tearDown
    account=flows.AccountFlows.account
    identity=flows.AccountFlows.identity

    def test_publication_and_contact_are_opt_in(self):
        uid,h=self.account()
        self.assertEqual(self.client.get(f'/portfolio/{uid}').status_code,404)
        data={'publico':True,'contacto_email':'contact@example.com','contacto_telefono':'+56912345678',
              'proyectos':[{'titulo':'Mi proyecto','github_url':'https://github.com/example/demo'}]}
        saved=self.client.put(f'/egresados/{uid}',headers=h,json={'portfolio':data,'presentacion':'Hola'})
        self.assertEqual(saved.status_code,200,saved.text)
        public=self.client.get(f'/portfolio/{uid}').json()
        self.assertEqual(public['portfolio']['contacto_email'],'')
        self.assertEqual(public['portfolio']['contacto_telefono'],'')
        self.assertNotIn('email',public)
        self.client.put('/portfolio/me',headers=h,json=data|{'mostrar_email':True})
        self.assertEqual(self.client.get(f'/portfolio/{uid}').json()['portfolio']['contacto_email'],'contact@example.com')
        self.client.put('/portfolio/me',headers=h,json=data|{'publico':False})
        self.assertEqual(self.client.get(f'/portfolio/{uid}').status_code,404)

    def test_media_ownership_verification_and_unpublication(self):
        uid,h=self.account()
        _,other=self.account(email='other@example.com')
        reserve=self.client.post('/media/reserve',headers=h,json={'tipo':'foto','nombre':'foto.png','mime':'image/png','tamano':200})
        self.assertEqual(reserve.status_code,201,reserve.text)
        aid=reserve.json()['id']
        data={'foto_id':aid,'publico':True}
        self.assertEqual(self.client.put('/portfolio/me',headers=h,json=data).status_code,422)
        self.assertEqual(self.client.get(f'/media/{aid}/access?upload=true',headers=other).status_code,404)
        self.assertEqual(self.client.post(f'/media/{aid}/verified',headers=h).status_code,403)
        with patch.dict('os.environ',{'MEDIA_SERVICE_SECRET':'isolated-test-service-key'}):
            self.assertEqual(self.client.post(f'/media/{aid}/verified',headers=h|{'X-Media-Service':'isolated-test-service-key'}).status_code,200)
        self.assertEqual(self.client.put('/portfolio/me',headers=other,json=data).status_code,422)
        self.assertEqual(self.client.get(f'/media/{aid}/access').status_code,404)
        self.assertEqual(self.client.put('/portfolio/me',headers=h,json=data).status_code,200)
        self.assertEqual(self.client.get(f'/media/{aid}/access').status_code,200)
        self.assertEqual(self.client.get(f'/media/{aid}/access?remove=true',headers=h).status_code,409)
        self.client.put('/portfolio/me',headers=h,json=data|{'publico':False})
        self.assertEqual(self.client.get(f'/media/{aid}/access').status_code,404)
        self.assertEqual(self.client.get(f'/media/{aid}/access',headers=h).status_code,200)

    def test_file_limits_and_nested_links(self):
        uid,h=self.account()
        base={'tipo':'presentacion','nombre':'intro.mp4','mime':'video/mp4','tamano':500,'duracion':60}
        for updates in [{'duracion':61},{'duracion':None},{'mime':'application/pdf'},{'tamano':16*1024*1024}]:
            self.assertEqual(self.client.post('/media/reserve',headers=h,json=base|updates).status_code,422)
        self.assertEqual(self.client.post('/media/reserve',headers=h,json=base).status_code,201)
        for data in [{'github_url':'javascript:alert(1)'},{'proyectos':[{'titulo':'x','video_url':'data:text/html,hi'}]},
                     {'certificaciones':[{'nombre':'Sin respaldo'}]},{'contacto_email':'no-es-email'}]:
            self.assertEqual(self.client.put('/portfolio/me',headers=h,json=data).status_code,422)
        with self.session() as db:
            self.assertEqual(db.query(ArchivoPortfolio).count(),1)

    def test_seed_is_exactly_100_idempotent_and_recommendations_match_career(self):
        uid,h=self.account()
        with self.session() as db:
            self.assertEqual(seed(db),100);db.commit()
            self.assertEqual(seed(db),0);db.commit()
            self.assertEqual(db.query(OfertaEmpleo).count(),100)
        for account in company_accounts():
            login = self.client.post('/auth/login', json={'email':account['correo'], 'password':account['contraseña']})
            self.assertEqual(login.status_code,200,login.text)
            company = login.json()['user']
            headers = {'Authorization':'Bearer '+login.json()['access_token']}
            summary = self.client.get(f"/empresas/{company['id']}/resumen",headers=headers)
            self.assertEqual(summary.status_code,200,summary.text)
            self.assertEqual(summary.json()['ofertas'],10)
        self.assertEqual(len({j['demo_clave'] for j in jobs()}),100)
        for career,expected in [('Ingeniería Civil en Informática','Tecnología'),('Enfermería','Salud'),('Diseño gráfico','Diseño y comunicación')]:
            self.client.put(f'/egresados/{uid}',headers=h,json={'carrera':career})
            response=self.client.get(f'/egresados/{uid}/recomendaciones',headers=h)
            self.assertEqual(response.status_code,200,response.text)
            selected=[j for j in response.json() if j['afin']]
            self.assertEqual(len(selected),10)
            self.assertTrue(all(j['categoria']==expected for j in selected))
        self.client.put(f'/egresados/{uid}',headers=h,json={'carrera':'Sin especialidad definida'})
        self.assertFalse(any(j['afin'] for j in self.client.get(f'/egresados/{uid}/recomendaciones',headers=h).json()))
