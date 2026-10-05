"""Integration tests against an isolated SQLite database; never touch local PostgreSQL."""
import os
import unittest
from datetime import datetime, timedelta, timezone

os.environ['DATABASE_URL'] = 'sqlite://'
os.environ['SECRET_KEY'] = 'isolated-test-key-never-use-in-production-12345'
os.environ['DATA_ENCRYPTION_KEY'] = 'YWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWE='

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from jose import jwt

from app.main import app
from app.database import Base, get_db
from app.models import Usuario
from app.rate_limit import limit_auth


class AccountFlows(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)

        def database():
            with self.session() as db:
                yield db
        app.dependency_overrides[get_db] = database
        app.dependency_overrides[limit_auth] = lambda: None
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.clear()
        self.engine.dispose()

    def account(self, role='egresado', email='persona@example.com'):
        data = {'email': email, 'password': 'Segura123!'}
        data.update({'nombre': 'Ana', 'apellido': 'Pérez'} if role == 'egresado' else {'nombre_empresa': 'Empresa de prueba'})
        response = self.client.post('/auth/registro/' + role, json=data)
        self.assertEqual(response.status_code, 201, response.text)
        login = self.client.post('/auth/login', json={'email': email, 'password': data['password']})
        self.assertEqual(login.status_code, 200, login.text)
        return response.json()['id'], {'Authorization': 'Bearer ' + login.json()['access_token']}

    def test_registration_login_profile_and_delete(self):
        user_id, headers = self.account()
        me = self.client.get('/auth/me', headers=headers)
        self.assertEqual(me.json()['id'], user_id)
        self.assertNotIn('password_hash', me.json())
        with self.session() as db:
            self.assertNotEqual(db.get(Usuario, user_id).password_hash, 'Segura123!')
        response = self.client.put(f'/egresados/{user_id}', headers=headers, json={'presentacion': 'Mi primer proyecto'})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()['presentacion'], 'Mi primer proyecto')
        self.assertEqual(self.client.delete(f'/egresados/{user_id}', headers=headers).status_code, 204)
        self.assertEqual(self.client.get('/auth/me', headers=headers).status_code, 401)

    def test_duplicate_and_invalid_credentials(self):
        self.account()
        duplicate = self.client.post('/auth/registro/egresado', json={'email': 'PERSONA@example.com', 'password': 'Segura123!', 'nombre': 'Ana', 'apellido': 'Pérez'})
        self.assertEqual(duplicate.status_code, 409)
        for email in ['persona@example.com', 'desconocido@example.com']:
            result = self.client.post('/auth/login', json={'email': email, 'password': 'incorrecta'})
            self.assertEqual(result.status_code, 401)
            self.assertEqual(result.json()['detail'], 'Correo o contraseña incorrectos.')

    def test_validations(self):
        data = {'email': 'ana@example.com', 'password': 'Segura123!', 'nombre': 'Ana', 'apellido': 'Pérez'}
        for invalid in [{'email': 'no-es-correo'}, {'password': 'corta'}, {'nombre': '  '}, {'password': 'ñ' * 40}]:
            self.assertEqual(self.client.post('/auth/registro/egresado', json=data | invalid).status_code, 422)
        user_id, headers = self.account()
        self.assertEqual(self.client.put(f'/egresados/{user_id}', headers=headers, json={'nombre': None}).status_code, 422)

    def test_jobs_and_authorization(self):
        company, headers = self.account('empresa', 'empresa@example.com')
        other, other_headers = self.account('empresa', 'otra@example.com')
        graduate, grad_headers = self.account()
        url = f'/empresas/{company}/ofertas'
        payload = {'titulo': 'Desarrollador junior', 'descripcion': 'Primera experiencia', 'modalidad': 'remoto'}
        self.assertEqual(self.client.post(url, json=payload).status_code, 401)
        self.assertEqual(self.client.post(url, json=payload, headers=grad_headers).status_code, 403)
        self.assertEqual(self.client.post(f'/empresas/{graduate}/ofertas', json=payload, headers=grad_headers).status_code, 403)
        result = self.client.post(url, json=payload, headers=headers)
        self.assertEqual(result.status_code, 201, result.text)
        job = result.json()['id']
        self.assertEqual(self.client.get(url, headers=other_headers).status_code, 403)
        self.assertEqual(self.client.put(f'/empresas/{other}/ofertas/{job}', headers=other_headers, json={'titulo': 'Intrusión'}).status_code, 404)
        self.assertEqual(self.client.get(f'/egresados/{graduate}', headers=headers).status_code, 403)
        public = self.client.get('/api/employment/jobs')
        self.assertEqual(public.status_code, 200, public.text)
        self.assertEqual(public.json()[0]['nombre_empresa'], 'Empresa de prueba')
        hub = self.client.get(f'/egresados/{graduate}/ofertas', headers=grad_headers)
        self.assertEqual(hub.status_code, 200, hub.text)
        self.assertEqual(self.client.put(url + f'/{job}', headers=headers, json={'activa': False}).status_code, 200)
        self.assertEqual(self.client.get('/api/employment/jobs').json(), [])
        self.assertEqual(self.client.delete(url + f'/{job}', headers=headers).status_code, 204)

    def test_expired_token_and_disabled_account(self):
        user_id, headers = self.account()
        expired = jwt.encode({'sub': str(user_id), 'exp': datetime.now(timezone.utc) - timedelta(minutes=1)}, os.environ['SECRET_KEY'], algorithm='HS256')
        for token in [expired, 'invalid']:
            self.assertEqual(self.client.get('/auth/me', headers={'Authorization': 'Bearer ' + token}).status_code, 401)
        with self.session() as db:
            db.get(Usuario, user_id).activo = False
            db.commit()
        self.assertEqual(self.client.get('/auth/me', headers=headers).status_code, 401)
        self.assertEqual(self.client.post('/auth/login', json={'email': 'persona@example.com', 'password': 'Segura123!'}).status_code, 401)


if __name__ == '__main__':
    unittest.main()
