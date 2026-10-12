import unittest
from unittest.mock import patch
import test_flows as flows
from app.models import Usuario


class CompanyIdentityFlows(unittest.TestCase):
    setUp = flows.AccountFlows.setUp
    tearDown = flows.AccountFlows.tearDown
    account = flows.AccountFlows.account
    identity = flows.AccountFlows.identity

    def test_registration_required_identity_and_private_data(self):
        for role, profile in [('egresado', {'nombre':'Ana','apellido':'Pérez','carrera':'Informática'}),
                              ('empresa', {'nombre_empresa':'Brote','rubro':'Tecnología'})]:
            data = {'email':role+'@example.com','password':'Segura123!', **self.identity(role), **profile}
            for field in ['rut', 'telefono', 'fecha_identidad', 'carrera' if role == 'egresado' else 'rubro']:
                missing = data.copy(); missing.pop(field)
                self.assertEqual(self.client.post('/auth/registro/'+role,json=missing).status_code,422)
            for invalid in [{'rut':'12.345.678-9'}, {'telefono':'abcdefgh'}, {'fecha_identidad':'2999-01-01'}]:
                self.assertEqual(self.client.post('/auth/registro/'+role,json=data|invalid).status_code,422)
            response = self.client.post('/auth/registro/'+role,json=data)
            self.assertEqual(response.status_code,201,response.text)
            self.assertNotIn('rut',response.json())
            self.assertNotIn('fecha_identidad',response.json())
            with self.session() as db:
                user = db.get(Usuario,response.json()['id'])
                self.assertEqual(user.rut,data['rut'])
                self.assertEqual(user.telefono,data['telefono'])
            duplicate = data | {'email':'different-'+role+'@example.com', 'rut':data['rut'].replace('-', '')}
            self.assertEqual(self.client.post('/auth/registro/'+role,json=duplicate).status_code,409)

    def test_company_edit_photo_ownership_and_removal(self):
        uid, headers = self.account('empresa')
        _, other = self.account('empresa','other@example.com')
        _, graduate = self.account('egresado','graduate@example.com')
        url = f'/empresas/{uid}/perfil'
        payload = {'nombre_empresa':'Nuevo nombre','descripcion':'Nuestro resumen'}
        for h, status in [({},401),(other,403),(graduate,403)]:
            self.assertEqual(self.client.put(url,headers=h,json=payload).status_code,status)
        self.assertEqual(self.client.put(url,headers=headers,json=payload|{'nombre_empresa':' '}).status_code,422)
        asset = self.client.post('/media/reserve',headers=headers,json={'tipo':'foto','nombre':'logo.png','mime':'image/png','tamano':200}).json()['id']
        payload['foto_id'] = asset
        self.assertEqual(self.client.put(url,headers=headers,json=payload).status_code,422)
        with patch.dict('os.environ',{'MEDIA_SERVICE_SECRET':'test-media-key'}):
            service_headers = headers | {'X-Media-Service':'test-media-key'}
            self.assertEqual(self.client.post(f'/media/{asset}/verified',headers=service_headers).status_code,200)
            self.assertEqual(self.client.put(url,headers=headers,json=payload).status_code,200)
            saved = self.client.get(url,headers=headers).json()
            self.assertEqual(saved['nombre_empresa'],'Nuevo nombre')
            self.assertEqual(saved['foto_id'],asset)
            self.assertEqual(self.client.put(f"/empresas/{self.client.get('/auth/me',headers=other).json()['id']}/perfil",headers=other,json=payload).status_code,422)
            self.assertEqual(self.client.get(f'/media/{asset}/access',headers=other).status_code,404)
            self.assertEqual(self.client.get(f'/media/{asset}/access?remove=true',headers=other).status_code,404)
            self.assertEqual(self.client.get(f'/media/{asset}/access',headers=headers).status_code,200)
            self.assertEqual(self.client.delete(f'/media/{asset}',headers=service_headers).status_code,409)
            self.client.put(url,headers=headers,json=payload|{'foto_id':None})
            self.assertEqual(self.client.delete(f'/media/{asset}',headers=service_headers).status_code,204)

    def test_password_change_invalidates_previous_sessions(self):
        _, headers = self.account('empresa')
        data = {'password_actual':'wrong','password':'NuevaSegura123!'}
        self.assertEqual(self.client.post('/auth/password',headers=headers,json=data).status_code,400)
        self.assertEqual(self.client.get('/auth/me',headers=headers).status_code,200)
        response = self.client.post('/auth/password',headers=headers,json=data|{'password_actual':'Segura123!'})
        self.assertEqual(response.status_code,200,response.text)
        self.assertEqual(self.client.get('/auth/me',headers=headers).status_code,401)
        fresh = {'Authorization':'Bearer '+response.json()['access_token']}
        self.assertEqual(self.client.get('/auth/me',headers=fresh).status_code,200)
        self.assertEqual(self.client.post('/auth/login',json={'email':'persona@example.com','password':'Segura123!'}).status_code,401)
        self.assertEqual(self.client.post('/auth/login',json={'email':'persona@example.com','password':'NuevaSegura123!'}).status_code,200)
