import unittest
from unittest.mock import patch
from fastapi import HTTPException
from sqlalchemy import text
import test_flows as flows
from app.main import app
from app import encryption
from app.models import Usuario, Postulacion
from app.rate_limit import RateLimiter, limit_auth


class SprintFlows(unittest.TestCase):
    setUp = flows.AccountFlows.setUp
    tearDown = flows.AccountFlows.tearDown
    account = flows.AccountFlows.account

    def offer(self, questions=None):
        company, headers = self.account('empresa', 'empresa@example.com')
        payload = {'titulo': 'Primer empleo', 'descripcion': 'Desarrollador junior', 'preguntas': questions or []}
        result = self.client.post(f'/empresas/{company}/ofertas', headers=headers, json=payload)
        self.assertEqual(result.status_code, 201, result.text)
        return company, headers, result.json()

    def application(self, job, answers=None):
        return {'oferta_id': job['id'], 'formulario_version': job['formulario_version'], 'telefono': '+56912345678',
                'mensaje': 'Me interesa este cargo', 'respuestas': answers or {}, 'consentimiento': True}

    def test_encrypted_application_and_company_read(self):
        question = {'id': 'motivo', 'etiqueta': '¿Qué puedes aportar?', 'tipo': 'parrafo', 'obligatoria': True, 'opciones': []}
        company, company_headers, job = self.offer([question])
        graduate, headers = self.account()
        data = self.application(job, {'motivo': 'Mi experiencia académica'})
        response = self.client.post('/api/employment/applications', headers=headers, json=data)
        self.assertEqual(response.status_code, 201, response.text)
        with self.session() as db:
            stored = db.execute(text('SELECT datos_cifrados FROM postulaciones')).scalar()
            self.assertNotIn('persona@example.com', stored)
            self.assertNotIn('Mi experiencia académica', stored)
            self.assertNotIn('+56912345678', stored)
            self.assertEqual(encryption.decrypt_data(stored)['respuestas']['motivo'], 'Mi experiencia académica')
        own = self.client.get('/api/employment/applications/me', headers=headers)
        self.assertEqual(len(own.json()), 1)
        received = self.client.get(f"/api/employment/jobs/{job['id']}/applications", headers=company_headers)
        self.assertEqual(received.status_code, 200, received.text)
        self.assertEqual(received.json()[0]['datos']['email'], 'persona@example.com')
        summary = self.client.get(f'/empresas/{company}/resumen', headers=company_headers).json()
        self.assertEqual((summary['ofertas'], summary['activas'], summary['postulaciones']), (1, 1, 1))
        self.assertEqual(self.client.post('/api/employment/applications', headers=headers, json=data).status_code, 409)
        self.assertEqual(self.client.delete(f"/empresas/{company}/ofertas/{job['id']}", headers=company_headers).status_code, 409)

    def test_access_isolation(self):
        company, owner_headers, job = self.offer()
        _, headers = self.account()
        self.assertEqual(self.client.post('/api/employment/applications', json=self.application(job)).status_code, 401)
        self.assertEqual(self.client.post('/api/employment/applications', headers=owner_headers, json=self.application(job)).status_code, 403)
        self.assertEqual(self.client.post('/api/employment/applications', headers=headers, json=self.application(job)).status_code, 201)
        _, other_company = self.account('empresa', 'otra@example.com')
        _, other_grad = self.account('egresado', 'otro@example.com')
        path = f"/api/employment/jobs/{job['id']}/applications"
        self.assertEqual(self.client.get(path, headers=other_company).status_code, 404)
        self.assertEqual(self.client.get(path, headers=headers).status_code, 403)
        self.assertEqual(self.client.get('/api/employment/applications/me', headers=other_grad).json(), [])
        self.assertEqual(self.client.get('/api/employment/applications/me', headers=owner_headers).status_code, 403)

    def test_required_questions_types_consent_and_closed_offer(self):
        questions = [{'id':'n','etiqueta':'Disponibilidad en días','tipo':'numero','obligatoria':True},
                     {'id':'s','etiqueta':'Jornada','tipo':'seleccion','obligatoria':True,'opciones':['Completa','Parcial']}]
        company, company_headers, job = self.offer(questions)
        _, headers = self.account()
        valid = self.application(job, {'n':'15','s':'Completa'})
        for updates in [{'respuestas':{}}, {'respuestas':{'n':'NaN','s':'Completa'}},
                        {'respuestas':{'n':'15','s':'Otra'}}, {'respuestas':{'n':'15','s':'Completa','extra':'x'}},
                        {'consentimiento':False}, {'cv_url':'javascript:alert(1)'}]:
            result = self.client.post('/api/employment/applications', headers=headers, json=valid | updates)
            self.assertEqual(result.status_code, 422, result.text)
        path = f"/empresas/{company}/ofertas/{job['id']}"
        changed = self.client.put(path, headers=company_headers, json={'preguntas':[]})
        self.assertEqual(changed.json()['formulario_version'], 2)
        self.assertEqual(self.client.post('/api/employment/applications', headers=headers, json=valid).status_code, 409)
        self.client.put(path, headers=company_headers, json={'activa':False})
        self.assertEqual(self.client.post('/api/employment/applications', headers=headers, json=self.application(changed.json())).status_code, 409)
        self.client.put(path, headers=company_headers, json={'activa':True})
        self.assertEqual(self.client.post('/api/employment/applications', headers=headers, json=self.application(changed.json())).status_code, 201)

    def test_presentation_delete_preserves_account_and_applications(self):
        _, _, job = self.offer()
        graduate, headers = self.account()
        url = f'/egresados/{graduate}/presentacion'
        self.assertEqual(self.client.post(url, headers=headers, json={'presentacion':'Mi presentación'}).status_code, 201)
        self.assertEqual(self.client.post(url, headers=headers, json={'presentacion':'Otra'}).status_code, 409)
        self.client.post('/api/employment/applications', headers=headers, json=self.application(job))
        self.assertEqual(self.client.delete(url, headers=headers).status_code, 204)
        self.assertEqual(self.client.get('/auth/me', headers=headers).status_code, 200)
        self.assertIsNone(self.client.get(f'/egresados/{graduate}', headers=headers).json()['presentacion'])
        snapshot = self.client.get('/api/employment/applications/me', headers=headers).json()[0]
        self.assertEqual(snapshot['datos']['presentacion'], 'Mi presentación')

    def test_logout_revokes_existing_sessions(self):
        graduate, headers = self.account()
        self.assertEqual(self.client.post('/auth/logout', headers=headers).status_code, 204)
        self.assertEqual(self.client.get('/auth/me', headers=headers).status_code, 401)
        login = self.client.post('/auth/login', json={'email':'persona@example.com','password':'Segura123!'})
        self.assertEqual(login.status_code, 200)
        self.assertEqual(self.client.get('/auth/me', headers={'Authorization':'Bearer '+login.json()['access_token']}).status_code, 200)

    def test_cipher_failure_does_not_store_plaintext(self):
        _, _, job = self.offer()
        _, headers = self.account()
        with patch.object(encryption, 'DATA_ENCRYPTION_KEY', ''):
            self.assertEqual(self.client.post('/api/employment/applications', headers=headers, json=self.application(job)).status_code, 503)
        with self.session() as db:
            self.assertEqual(db.query(Postulacion).count(), 0)
        encrypted = encryption.encrypt_data({'private':'value'})
        with self.assertRaises(HTTPException):
            encryption.decrypt_data(encrypted[:-8] + 'tampered')

    def test_security_headers_and_validation_redaction(self):
        result = self.client.post('/auth/login', json={'email':'invalid','password':'do-not-echo-this'})
        self.assertEqual(result.status_code, 422)
        self.assertNotIn('do-not-echo-this', result.text)
        self.assertEqual(result.headers['cache-control'], 'no-store')
        self.assertEqual(result.headers['x-content-type-options'], 'nosniff')

    def test_rate_limit_and_recovery(self):
        limited = RateLimiter(limit=2, seconds=60)
        limited.check('test', now=0)
        limited.check('test', now=1)
        with self.assertRaises(HTTPException) as exc:
            limited.check('test', now=2)
        self.assertEqual(exc.exception.status_code, 429)
        limited.check('test', now=62)
        # Also prove the route executes the limiter dependency.
        def reject():
            raise HTTPException(429, 'Espera', headers={'Retry-After':'60'})
        app.dependency_overrides[limit_auth] = reject
        result = self.client.post('/auth/login', json={'email':'persona@example.com','password':'Segura123!'})
        self.assertEqual(result.status_code, 429)
        self.assertEqual(result.headers['retry-after'], '60')

    def test_question_configuration_validation_and_snapshot(self):
        company, headers, job = self.offer([{'id':'q1','etiqueta':'Pregunta inicial','tipo':'texto','obligatoria':False}])
        path = f"/empresas/{company}/ofertas/{job['id']}"
        invalids = [None, [{'id':'dup','etiqueta':'Uno'},{'id':'dup','etiqueta':'Dos'}],
                    [{'id':'x','etiqueta':'Selecciona','tipo':'seleccion','opciones':['Única']}],
                    [{'id':'x','etiqueta':'  '}]]
        for questions in invalids:
            result = self.client.put(path, headers=headers, json={'preguntas':questions})
            self.assertEqual(result.status_code, 422, result.text)
        _, graduate = self.account()
        self.client.post('/api/employment/applications', headers=graduate, json=self.application(job, {'q1':'Respuesta original'}))
        self.client.put(path, headers=headers, json={'preguntas':[{'id':'q1','etiqueta':'Pregunta modificada','tipo':'texto'}]})
        stored = self.client.get('/api/employment/applications/me', headers=graduate).json()[0]
        self.assertEqual(stored['datos']['preguntas'][0]['etiqueta'], 'Pregunta inicial')
        self.assertEqual(stored['datos']['respuestas']['q1'], 'Respuesta original')
