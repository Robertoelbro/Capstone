"""No client-controlled payment signal can activate a subscription."""
from datetime import datetime, timedelta, timezone
import unittest
from unittest.mock import patch

import test_flows as flows
from app.subscription_models import Subscription, has_subscription


class BillingTests(unittest.TestCase):
    setUp = flows.AccountFlows.setUp
    tearDown = flows.AccountFlows.tearDown
    account = flows.AccountFlows.account
    identity = flows.AccountFlows.identity

    def test_status_role_and_identity_isolation(self):
        user, headers = self.account()
        _, other = self.account('egresado', 'other@example.com')
        _, company = self.account('empresa', 'company@example.com')
        self.assertEqual(self.client.get('/billing/me').status_code, 401)
        self.assertEqual(self.client.get('/billing/me', headers=company).status_code, 403)
        self.assertEqual(self.client.post('/billing/checkout', headers=company).status_code, 403)
        with self.session() as db:
            db.add(Subscription(usuario_id=user, estado='activa', vigente_hasta=datetime.now(timezone.utc) + timedelta(days=30)))
            db.commit()
        self.assertEqual(self.client.get('/billing/me', headers=headers).json()['estado'], 'activa')
        self.assertEqual(self.client.get('/billing/me', headers=other).json()['estado'], 'inactiva')

    def test_default_contract_and_keys_are_never_returned(self):
        _, headers = self.account()
        with patch.dict('os.environ', {'WEBPAY_COMMERCE_CODE': 'private-code', 'WEBPAY_API_KEY': 'private-secret',
                                       'WEBPAY_ENV': 'integration', 'WEBPAY_ENABLED': 'true'}):
            result = self.client.get('/billing/me', headers=headers)
        self.assertEqual(result.status_code, 200, result.text)
        data = result.json()
        self.assertEqual((data['precio_clp'], data['periodicidad'], data['pasarela']), (2990, 'mensual', 'Webpay'))
        self.assertEqual(data['estado'], 'inactiva')
        self.assertIsNone(data['vigente_hasta'])
        self.assertEqual(data['beneficios'], ['Prácticas de entrevista sin límite diario de BranchIT',
                                             'Candidato destacado en tus postulaciones'])
        self.assertFalse(data['pago_habilitado'])
        self.assertTrue(data['configuracion_pendiente'])
        self.assertNotIn('private-code', result.text)
        self.assertNotIn('private-secret', result.text)

    def test_expired_or_missing_expiration_never_grants_active_status(self):
        user, headers = self.account()
        with self.session() as db:
            row = Subscription(usuario_id=user, estado='activa', vigente_hasta=datetime.now(timezone.utc) - timedelta(seconds=1))
            db.add(row)
            db.commit()
        self.assertEqual(self.client.get('/billing/me', headers=headers).json()['estado'], 'inactiva')
        with self.session() as db:
            self.assertFalse(has_subscription(db, user))
        with self.session() as db:
            db.query(Subscription).filter_by(usuario_id=user).update({'vigente_hasta': None})
            db.commit()
        self.assertEqual(self.client.get('/billing/me', headers=headers).json()['estado'], 'inactiva')

    def test_entitlement_helper_requires_active_future_own_record(self):
        user, _ = self.account()
        with self.session() as db:
            self.assertFalse(has_subscription(db, user))
            row = Subscription(usuario_id=user, estado='activa', vigente_hasta=datetime.now(timezone.utc) + timedelta(days=30))
            db.add(row)
            db.commit()
            self.assertTrue(has_subscription(db, user))
            self.assertFalse(has_subscription(db, user + 100))
            row.estado = 'inactiva'
            db.commit()
            self.assertFalse(has_subscription(db, user))

    def test_checkout_fails_closed_and_cannot_be_activated_by_browser(self):
        user, headers = self.account()
        self.assertEqual(self.client.post('/billing/checkout').status_code, 401)
        with patch.dict('os.environ', {'WEBPAY_ENABLED': 'true', 'WEBPAY_API_KEY': 'not-a-real-key',
                                       'WEBPAY_COMMERCE_CODE': 'not-a-real-code'}):
            result = self.client.post('/billing/checkout?approved=true&amount=1', headers=headers,
                json={'usuario_id': user, 'estado': 'activa', 'token_ws': 'fake', 'precio_clp': 1})
        self.assertEqual(result.status_code, 503, result.text)
        self.assertIn('No se ha realizado ningún cobro', result.json()['detail'])
        with self.session() as db:
            self.assertEqual(db.query(Subscription).count(), 0)
        self.assertEqual(self.client.post('/billing/return?token_ws=fake', headers=headers).status_code, 404)
        self.assertEqual(self.client.put('/billing/me', headers=headers, json={'estado': 'activa'}).status_code, 405)
