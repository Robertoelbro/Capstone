import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import test_flows as flows
import test_ai_daily as daily_tests
from test_offer_forms import DETAILS
from app.models import EntrevistaIA, SeguimientoLaboral
from app.encryption import encrypt_data
from app.subscription_models import Subscription


class SubscriptionBenefitTests(unittest.TestCase):
    setUp = flows.AccountFlows.setUp
    tearDown = flows.AccountFlows.tearDown
    account = flows.AccountFlows.account
    identity = flows.AccountFlows.identity
    offer = daily_tests.DailyAssistantTests.offer
    request = daily_tests.DailyAssistantTests.request

    def subscribe(self, uid, days=1):
        with self.session() as db:
            db.add(Subscription(usuario_id=uid, estado='activa', vigente_hasta=datetime.now(timezone.utc) + timedelta(days=days)))
            db.commit()

    def test_paid_can_start_multiple_sessions_and_cannot_forge_other_history(self):
        job = self.offer()
        uid, headers = self.account()
        self.subscribe(uid)
        _, other = self.account('egresado', 'other@example.com')
        payload = self.request(modo='entrevista', borrador='', oferta_id=job)
        with patch('app.routers.assistant.generate', return_value={'respuesta': 'Pregunta', 'incompleta': False}):
            first = self.client.post('/assistant/chat', headers=headers, json=payload)
            second = self.client.post('/assistant/chat', headers=headers, json=payload)
            self.assertEqual(first.status_code, 200, first.text)
            self.assertEqual(second.status_code, 200, second.text)
            self.assertNotEqual(first.json()['entrevista']['id'], second.json()['entrevista']['id'])
            latest = self.client.get('/assistant/status', headers=headers).json()
            self.assertTrue(latest['entrevistas_ilimitadas'])
            self.assertEqual(latest['entrevista_hoy']['id'], second.json()['entrevista']['id'])
            self.assertEqual(self.client.post('/assistant/chat', headers=other,
                json=payload | {'entrevista_id': first.json()['entrevista']['id']}).status_code, 404)
        with self.session() as db:
            self.assertEqual(db.query(EntrevistaIA).count(), 2)

    def test_expired_subscription_does_not_remove_free_daily_limit(self):
        job = self.offer()
        uid, headers = self.account()
        self.subscribe(uid, days=-1)
        payload = self.request(modo='entrevista', borrador='', oferta_id=job)
        with patch('app.routers.assistant.generate', return_value={'respuesta': 'Pregunta', 'incompleta': False}):
            self.assertEqual(self.client.post('/assistant/chat', headers=headers, json=payload).status_code, 200)
            self.assertEqual(self.client.post('/assistant/chat', headers=headers, json=payload).status_code, 429)
        self.assertFalse(self.client.get('/assistant/status', headers=headers).json()['entrevistas_ilimitadas'])

    def test_highlight_uses_same_label_without_revealing_subscription_or_altering_affinity(self):
        cid, company = self.account('empresa', 'company@example.com')
        uid, graduate = self.account()
        self.client.put(f'/egresados/{uid}', headers=graduate, json={'carrera': 'Gastronomía'})
        self.subscribe(uid)
        job = self.client.post(f'/empresas/{cid}/ofertas', headers=company,
            json={'titulo': 'Cargo', 'descripcion': 'Sin coincidencias', **DETAILS}).json()
        applied = self.client.post('/api/employment/applications', headers=graduate,
            json={'oferta_id': job['id'], 'formulario_version': 1, 'consentimiento': True})
        self.assertEqual(applied.status_code, 201, applied.text)
        result = self.client.get(f"/api/employment/jobs/{job['id']}/applications", headers=company)
        self.assertEqual(result.status_code, 200, result.text)
        self.assertTrue(result.json()[0]['destacado'])
        self.assertEqual(result.json()[0]['afinidad']['puntos'], 0)
        for field in ('suscripcion', 'subscription', 'premium', 'pagador', 'vigente_hasta'):
            self.assertNotIn(field, result.text)

    def test_subscription_does_not_bypass_experience_gate_or_remove_portfolio_access(self):
        job = self.offer()
        uid, headers = self.account()
        self.subscribe(uid)
        with self.session() as db:
            db.add(SeguimientoLaboral(usuario_id=uid, situacion='buscando', busqueda_activa=False,
                                     limite_experiencia=True, datos_cifrados=encrypt_data({})))
            db.commit()
        self.assertEqual(self.client.get('/billing/me', headers=headers).json()['estado'], 'activa')
        self.assertTrue(self.client.get('/assistant/status', headers=headers).json()['entrevistas_ilimitadas'])
        result = self.client.post('/api/employment/applications', headers=headers,
            json={'oferta_id': job, 'formulario_version': 1, 'consentimiento': True})
        self.assertEqual(result.status_code, 409, result.text)
        result = self.client.put('/portfolio/me', headers=headers, json={'titular': 'Mi portafolio sigue disponible'})
        self.assertEqual(result.status_code, 200, result.text)
