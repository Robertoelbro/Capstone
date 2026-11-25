"""Employment state is private and controls only new applications."""
import json
import unittest
from datetime import date, timedelta

import test_flows as flows
from test_offer_forms import DETAILS
from app.models import Postulacion, SeguimientoLaboral, Usuario, OfertaEmpleo
from app.models import ArchivoPortfolio
from uuid import uuid4


class EmploymentTests(unittest.TestCase):
    setUp = flows.AccountFlows.setUp
    tearDown = flows.AccountFlows.tearDown
    account = flows.AccountFlows.account
    identity = flows.AccountFlows.identity

    def job(self, company, headers):
        result = self.client.post(f'/empresas/{company}/ofertas', headers=headers,
            json={'titulo': 'Cargo de prueba', 'descripcion': 'Primera experiencia', **DETAILS})
        self.assertEqual(result.status_code, 201, result.text)
        return result.json()

    def apply(self, job, headers):
        return self.client.post('/api/employment/applications', headers=headers,
            json={'oferta_id': job['id'], 'formulario_version': job['formulario_version'], 'consentimiento': True})

    def test_private_encrypted_state_and_role_isolation(self):
        user, headers = self.account()
        _, company = self.account('empresa', 'company@example.com')
        _, other = self.account('egresado', 'other@example.com')
        self.assertEqual(self.client.get('/employment/me').status_code, 401)
        self.assertEqual(self.client.get('/employment/me', headers=company).status_code, 403)
        self.assertEqual(self.client.put('/employment/me', headers=company,
            json={'situacion': 'buscando', 'busqueda_activa': True}).status_code, 403)
        default = self.client.get('/employment/me', headers=headers).json()
        self.assertEqual((default['situacion'], default['busqueda_activa']), ('buscando', True))
        result = self.client.put('/employment/me', headers=headers, json={
            'situacion': 'trabajando', 'busqueda_activa': True,
            'empresa': 'Empresa confidencial', 'cargo': 'Cargo privado', 'fecha_inicio': '2026-01-01'})
        self.assertEqual(result.status_code, 200, result.text)
        self.assertFalse(result.json()['busqueda_activa'])
        self.assertEqual(self.client.get('/employment/me', headers=headers).json()['empresa'], 'Empresa confidencial')
        self.assertIsNone(self.client.get('/employment/me', headers=other).json()['empresa'])
        with self.session() as db:
            row = db.query(SeguimientoLaboral).filter_by(usuario_id=user).one()
            self.assertNotIn('Empresa confidencial', row.datos_cifrados)
            self.assertNotIn('Cargo privado', row.datos_cifrados)
        self.assertNotIn('confidencial', self.client.get(f'/egresados/{user}', headers=headers).text)

    def test_working_and_pause_block_new_applications_then_resume(self):
        company, owner = self.account('empresa', 'company@example.com')
        _, headers = self.account()
        job = self.job(company, owner)
        for data in ({'situacion': 'buscando', 'busqueda_activa': False},):
            self.assertEqual(self.client.put('/employment/me', headers=headers, json=data).status_code, 200)
            self.assertEqual(self.apply(job, headers).status_code, 409)
        self.assertEqual(self.client.put('/employment/me', headers=headers,
            json={'situacion': 'buscando', 'busqueda_activa': True}).status_code, 200)
        self.assertEqual(self.client.put('/employment/me', headers=headers,
            json={'situacion': 'trabajando', 'busqueda_activa': True, 'fecha_inicio': '2026-01-01'}).status_code, 200)
        self.assertEqual(self.apply(job, headers).status_code, 409)
        self.assertEqual(self.client.put('/employment/me', headers=headers,
            json={'situacion': 'buscando', 'busqueda_activa': True}).status_code, 409)
        user_id = self.client.get('/auth/me', headers=headers).json()['id']
        asset_id = uuid4().hex
        with self.session() as db:
            db.add(ArchivoPortfolio(id=asset_id, usuario_id=user_id, tipo='finiquito', nombre='finiquito.pdf',
                mime='application/pdf', tamano=100, pathname=f'test/{asset_id}.pdf', verificado=True))
            db.commit()
        self.assertEqual(self.client.post('/employment/release', headers=headers, json={
            'archivo_id': asset_id, 'fecha_fin': '2026-02-01', 'motivo': 'renuncia'}).status_code, 200)
        self.assertEqual(self.apply(job, headers).status_code, 201)
        self.assertEqual(len(self.client.get('/api/employment/applications/me', headers=headers).json()), 1)

    def test_follow_up_cannot_link_foreign_application_or_future_date(self):
        company, owner = self.account('empresa', 'company@example.com')
        _, first = self.account()
        _, second = self.account('egresado', 'other@example.com')
        job = self.job(company, owner)
        application = self.apply(job, first).json()['id']
        working = {'situacion': 'trabajando', 'busqueda_activa': False, 'postulacion_id': application, 'fecha_inicio': '2026-01-01'}
        self.assertEqual(self.client.put('/employment/me', headers=second, json=working).status_code, 422)
        result = self.client.put('/employment/me', headers=first, json=working)
        self.assertEqual(result.status_code, 200, result.text)
        self.assertNotIn('seleccionada', result.text)
        self.assertEqual(self.client.put('/employment/me', headers=first,
            json=working | {'fecha_inicio': str(date.today() + timedelta(days=1))}).status_code, 422)
        self.assertEqual(self.client.put('/employment/me', headers=first,
            json={'situacion': 'buscando', 'busqueda_activa': True, 'empresa': 'No válida'}).status_code, 422)

    def test_graduate_deactivation_hides_profile_revokes_all_sessions_and_preserves_data(self):
        user, headers = self.account()
        second = self.client.post('/auth/login', json={'email': 'persona@example.com', 'password': 'Segura123!'}).json()
        second_headers = {'Authorization': 'Bearer ' + second['access_token']}
        self.assertEqual(self.client.put('/portfolio/me', headers=headers, json={'publico': True}).status_code, 200)
        self.assertEqual(self.client.get(f'/portfolio/{user}').status_code, 200)
        self.assertEqual(self.client.post('/auth/deactivate', headers=headers, json={'password_actual': 'wrong'}).status_code, 400)
        self.assertEqual(self.client.get('/auth/me', headers=headers).status_code, 200)
        self.assertEqual(self.client.post('/auth/deactivate', headers=headers, json={'password_actual': 'Segura123!'}).status_code, 204)
        self.assertEqual(self.client.get('/auth/me', headers=headers).status_code, 401)
        self.assertEqual(self.client.get('/auth/me', headers=second_headers).status_code, 401)
        self.assertEqual(self.client.get(f'/portfolio/{user}').status_code, 404)
        self.assertEqual(self.client.post('/auth/login', json={'email': 'persona@example.com', 'password': 'Segura123!'}).status_code, 401)
        with self.session() as db:
            self.assertIsNotNone(db.get(Usuario, user).perfil_egresado)
            self.assertFalse(db.get(Usuario, user).activo)

    def test_company_deactivation_closes_calls_and_notifies_without_exposing_selection(self):
        company, owner = self.account('empresa', 'company@example.com')
        _, graduate = self.account()
        job = self.job(company, owner)
        application = self.apply(job, graduate)
        self.assertEqual(application.status_code, 201, application.text)
        result = self.client.post('/auth/deactivate', headers=owner, json={'password_actual': 'Segura123!'})
        self.assertEqual(result.status_code, 204, result.text)
        self.assertEqual(self.client.get('/api/employment/jobs').json(), [])
        self.assertEqual(self.client.get(f"/api/employment/jobs/{job['id']}").status_code, 404)
        history = self.client.get('/api/employment/applications/me', headers=graduate).json()
        self.assertEqual(history[0]['estado'], 'cerrada')
        self.assertNotIn('seleccionada', json.dumps(history))
        notices = self.client.get('/notifications', headers=graduate).json()
        self.assertTrue(any('se cerró' in item['mensaje'] for item in notices['items']))
        with self.session() as db:
            self.assertFalse(db.get(OfertaEmpleo, job['id']).activa)
            self.assertEqual(db.query(Postulacion).count(), 1)

    def test_inactive_company_filtered_even_if_offer_flag_is_still_active(self):
        company, owner = self.account('empresa', 'company@example.com')
        graduate_id, graduate = self.account()
        job = self.job(company, owner)
        with self.session() as db:
            db.get(Usuario, company).activo = False
            db.commit()
        self.assertEqual(self.client.get('/api/employment/jobs').json(), [])
        self.assertEqual(self.client.get(f'/egresados/{graduate_id}/ofertas', headers=graduate).json(), [])
        self.assertEqual(self.client.get(f'/egresados/{graduate_id}/recomendaciones', headers=graduate).json(), [])
        self.assertEqual(self.apply(job, graduate).status_code, 409)
