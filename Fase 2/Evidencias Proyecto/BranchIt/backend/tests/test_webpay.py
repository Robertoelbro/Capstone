"""Webpay integration protocol using a fake provider; never contact Transbank."""
from datetime import datetime, timedelta, timezone
import json
import unittest
from unittest.mock import patch
from uuid import uuid4

import test_flows as flows
from app.subscription_models import Subscription, WebpayOrder
from app.webpay import PAYMENT_URL, PaymentProviderError, WebpayProvider, WebpaySettings, settings
from app.routers.billing import calendar_month


class FakeProvider:
    def __init__(self):
        self.records = {}
        self.creates = self.commits = 0
        self.create_timeout = self.commit_timeout = self.status_error = False
        self.error_after_commit = False

    def create(self, order):
        self.creates += 1
        if self.create_timeout:
            raise PaymentProviderError()
        token = uuid4().hex * 2
        self.records[token] = {'buy_order': order.buy_order, 'session_id': order.session_id,
            'amount': order.monto_clp, 'status': 'INITIALIZED', 'response_code': -1}
        return {'url': PAYMENT_URL, 'token': token}

    def status(self, token):
        if self.status_error or (self.error_after_commit and self.commits):
            raise PaymentProviderError()
        return dict(self.records[token])

    def commit(self, token):
        self.commits += 1
        self.records[token].update(status='AUTHORIZED', response_code=0)
        if self.commit_timeout:
            raise PaymentProviderError()
        return dict(self.records[token])


class WebpayTests(unittest.TestCase):
    account = flows.AccountFlows.account
    identity = flows.AccountFlows.identity

    def setUp(self):
        flows.AccountFlows.setUp(self)
        self.fake = FakeProvider()
        self.env = patch.dict('os.environ', {
            'WEBPAY_ENABLED': 'true', 'WEBPAY_ENV': 'integration',
            'WEBPAY_COMMERCE_CODE': '597055555532', 'WEBPAY_API_KEY': 'a' * 64,
            'WEBPAY_RETURN_URL': 'https://api.example.invalid/billing/return',
            'WEBPAY_FRONTEND_URL': 'http://localhost:5173'})
        self.env.start()
        self.origins = patch('app.webpay.CORS_ORIGINS', ['http://localhost:5173'])
        self.origins.start()
        self.provider = patch('app.routers.billing.provider_for', return_value=self.fake)
        self.provider.start()

    def tearDown(self):
        self.provider.stop()
        self.origins.stop()
        self.env.stop()
        flows.AccountFlows.tearDown(self)

    def checkout(self, headers, request_id=None):
        result = self.client.post('/billing/checkout', headers=headers, json={'request_id': request_id or str(uuid4())})
        self.assertEqual(result.status_code, 200, result.text)
        return result.json()

    def callback(self, token, **extra):
        return self.client.get('/billing/return', params={'token_ws': token, **extra}, follow_redirects=False)

    def test_checkout_server_price_encrypted_token_and_idempotent_request(self):
        user, headers = self.account()
        request_id = str(uuid4())
        first = self.checkout(headers, request_id)
        again = self.checkout(headers, request_id)
        self.assertEqual(first, again)
        self.assertEqual(self.fake.creates, 1)
        self.assertEqual(first['url'], PAYMENT_URL)
        with self.session() as db:
            order = db.get(WebpayOrder, first['order_id'])
            self.assertEqual(order.monto_clp, 2990)
            self.assertNotIn(first['token'], order.datos_cifrados)
            self.assertEqual(len(order.buy_order), 26)
            self.assertEqual(order.usuario_id, user)
            self.assertEqual(db.query(Subscription).count(), 0)
        result = self.client.post('/billing/checkout', headers=headers,
            json={'request_id': str(uuid4()), 'amount': 1, 'estado': 'activa', 'usuario_id': user})
        self.assertEqual(result.status_code, 422)
        self.assertEqual(self.fake.creates, 1)

    def test_callback_approval_grants_one_calendar_month_only_once_without_leaking_token(self):
        user, headers = self.account()
        order = self.checkout(headers)
        with patch('app.routers.billing.now', return_value=datetime(2026, 1, 31, 14, tzinfo=timezone.utc)):
            first = self.callback(order['token'])
            again = self.callback(order['token'])
            reconcile = self.client.post(f"/billing/orders/{order['order_id']}/reconcile", headers=headers)
        self.assertEqual((first.status_code, again.status_code, reconcile.status_code), (303, 303, 200))
        self.assertEqual(first.headers['location'], f"http://localhost:5173/suscripcion?orden={order['order_id']}")
        self.assertNotIn(order['token'], first.headers['location'])
        self.assertEqual(self.fake.commits, 1)
        with self.session() as db:
            subscription = db.query(Subscription).filter_by(usuario_id=user).one()
            self.assertEqual(subscription.vigente_hasta.date().isoformat(), '2026-02-28')
            self.assertTrue(db.get(WebpayOrder, order['order_id']).beneficio_aplicado)
        view = self.client.get(f"/billing/orders/{order['order_id']}", headers=headers)
        self.assertNotIn(order['token'], view.text)
        self.assertNotIn('token_digest', view.text)

    def test_order_ownership_and_query_flags_cannot_activate_entitlement(self):
        _, first = self.account()
        _, other = self.account('egresado', 'other@example.com')
        _, company = self.account('empresa', 'company@example.com')
        order = self.checkout(first)
        for path in (f"/billing/orders/{order['order_id']}",):
            self.assertEqual(self.client.get(path).status_code, 401)
            self.assertEqual(self.client.get(path, headers=other).status_code, 404)
            self.assertEqual(self.client.get(path, headers=company).status_code, 403)
        self.assertEqual(self.client.post(f"/billing/orders/{order['order_id']}/reconcile", headers=other).status_code, 404)
        view = self.client.post(f"/billing/orders/{order['order_id']}/reconcile?approved=true&amount=1", headers=first)
        self.assertEqual(view.status_code, 200)
        self.assertEqual(view.json()['estado'], 'pendiente')
        self.assertFalse(view.json()['beneficio_aplicado'])
        self.assertEqual(self.fake.commits, 0)

    def test_provider_amount_order_session_and_exact_response_code_are_required(self):
        _, headers = self.account()
        for modified in ({'amount': 1}, {'buy_order': 'otra'}, {'session_id': 'otra'},
                         {'response_code': False}, {'response_code': '0'}, {'status': 'FAILED'}):
            order = self.checkout(headers)
            self.fake.records[order['token']].update({'status': 'AUTHORIZED', 'response_code': 0, **modified})
            result = self.callback(order['token'])
            self.assertEqual(result.status_code, 303)
            view = self.client.get(f"/billing/orders/{order['order_id']}", headers=headers).json()
            self.assertFalse(view['beneficio_aplicado'], modified)
        with self.session() as db:
            self.assertEqual(db.query(Subscription).count(), 0)

    def test_cancel_post_and_invalid_or_duplicate_tokens_never_commit(self):
        _, headers = self.account()
        order = self.checkout(headers)
        cancelled = self.client.post('/billing/return', data={'TBK_TOKEN': order['token']}, follow_redirects=False)
        self.assertEqual(cancelled.status_code, 303)
        view = self.client.get(f"/billing/orders/{order['order_id']}", headers=headers).json()
        self.assertEqual(view['estado'], 'cancelada')
        self.assertFalse(view['beneficio_aplicado'])
        self.assertEqual(self.fake.commits, 0)
        self.assertEqual(self.client.get('/billing/return', params={'token_ws': 'f' * 64}).status_code, 404)
        self.assertEqual(self.client.get('/billing/return?token_ws=' + order['token'] + '&token_ws=' + order['token']).status_code, 400)

    def test_commit_timeout_recovers_authorization_by_status_and_can_be_reconciled_later(self):
        _, headers = self.account()
        self.fake.commit_timeout = True
        first = self.checkout(headers)
        self.assertEqual(self.callback(first['token']).status_code, 303)
        self.assertTrue(self.client.get(f"/billing/orders/{first['order_id']}", headers=headers).json()['beneficio_aplicado'])
        second = self.checkout(headers)
        self.fake.error_after_commit = True
        # Reset fake count so initial status succeeds and only post-commit read fails.
        self.fake.commits = 0
        self.assertEqual(self.callback(second['token']).status_code, 303)
        self.assertEqual(self.client.get(f"/billing/orders/{second['order_id']}", headers=headers).json()['estado'], 'incierta')
        self.fake.error_after_commit = False
        view = self.client.post(f"/billing/orders/{second['order_id']}/reconcile", headers=headers)
        self.assertTrue(view.json()['beneficio_aplicado'])
        self.assertEqual(self.fake.commits, 1)

    def test_create_timeout_retains_order_and_same_request_never_repeats_create(self):
        _, headers = self.account()
        self.fake.create_timeout = True
        request_id = str(uuid4())
        first = self.checkout(headers, request_id)
        again = self.checkout(headers, request_id)
        self.assertEqual(first['order_id'], again['order_id'])
        self.assertEqual(first['estado'], 'incierta')
        self.assertIsNone(first['token'])
        self.assertEqual(self.fake.creates, 1)
        self.assertFalse(self.client.get(f"/billing/orders/{first['order_id']}", headers=headers).json()['puede_reconciliar'])

    def test_expired_callback_and_crashed_create_can_be_recovered_without_new_commit(self):
        _, headers = self.account()
        order = self.checkout(headers)
        with self.session() as db:
            row = db.get(WebpayOrder, order['order_id'])
            buy_order, session_id = row.buy_order, row.session_id
        timeout = self.client.get('/billing/return', params={'TBK_ORDEN_COMPRA': buy_order, 'TBK_ID_SESION': session_id}, follow_redirects=False)
        self.assertEqual(timeout.status_code, 303)
        self.assertEqual(self.client.get(f"/billing/orders/{order['order_id']}", headers=headers).json()['estado'], 'expirada')
        self.assertEqual(self.fake.commits, 0)
        with self.session() as db:
            row = db.get(WebpayOrder, order['order_id'])
            row.estado, row.token_digest, row.datos_cifrados = 'creando', None, None
            row.creada = datetime.now(timezone.utc) - timedelta(minutes=3)
            db.commit()
        stale = self.client.get(f"/billing/orders/{order['order_id']}", headers=headers).json()
        self.assertEqual(stale['estado'], 'incierta')
        self.assertFalse(stale['puede_reconciliar'])

    def test_callback_order_hints_and_mixed_tokens_are_checked(self):
        _, headers = self.account()
        order = self.checkout(headers)
        self.assertEqual(self.callback(order['token'], TBK_ORDEN_COMPRA='forged').status_code, 400)
        self.assertEqual(self.callback(order['token'], TBK_TOKEN='f' * 64).status_code, 404)
        mixed = self.callback(order['token'], TBK_TOKEN=order['token'])
        self.assertEqual(mixed.status_code, 303)
        self.assertEqual(self.fake.commits, 0)

    def test_stale_pending_token_is_not_reused_or_reported_as_financial_rejection(self):
        _, headers = self.account()
        first = self.checkout(headers)
        with self.session() as db:
            row = db.get(WebpayOrder, first['order_id'])
            request_id = row.request_id
            row.creada = datetime.now(timezone.utc) - timedelta(minutes=20)
            db.commit()
        again = self.checkout(headers, request_id)
        self.assertEqual(again['order_id'], first['order_id'])
        self.assertEqual(again['estado'], 'incierta')
        self.assertIsNone(again['token'])
        self.assertIsNone(again['url'])
        self.assertEqual(self.fake.creates, 1)
        status = self.client.get(f"/billing/orders/{first['order_id']}", headers=headers).json()
        self.assertEqual(status['estado'], 'incierta')
        self.assertTrue(status['puede_reconciliar'])
        reconciled = self.client.post(f"/billing/orders/{first['order_id']}/reconcile", headers=headers).json()
        self.assertEqual(reconciled['estado'], 'incierta')
        self.assertFalse(reconciled['beneficio_aplicado'])
        self.assertEqual(self.fake.commits, 0)

    def test_stale_order_authorized_later_is_fulfilled_exactly_once(self):
        _, headers = self.account()
        order = self.checkout(headers)
        with self.session() as db:
            row = db.get(WebpayOrder, order['order_id'])
            row.creada = datetime.now(timezone.utc) - timedelta(minutes=20)
            db.commit()
        self.fake.records[order['token']].update(status='AUTHORIZED', response_code=0)
        first = self.client.post(f"/billing/orders/{order['order_id']}/reconcile", headers=headers).json()
        self.assertTrue(first['beneficio_aplicado'])
        self.assertEqual(first['estado'], 'autorizada')
        self.assertEqual(self.callback(order['token']).status_code, 303)
        again = self.client.post(f"/billing/orders/{order['order_id']}/reconcile", headers=headers).json()
        self.assertEqual(first['vigente_hasta'], again['vigente_hasta'])
        self.assertEqual(self.fake.commits, 0)
        with self.session() as db:
            self.assertEqual(db.query(Subscription).count(), 1)

    def test_active_subscription_manual_renewal_extends_from_current_expiration(self):
        user, headers = self.account()
        with self.session() as db:
            db.add(Subscription(usuario_id=user, estado='activa', vigente_hasta=datetime(2027, 12, 31, tzinfo=timezone.utc)))
            db.commit()
        order = self.checkout(headers)
        self.callback(order['token'])
        with self.session() as db:
            self.assertEqual(db.query(Subscription).one().vigente_hasta.date().isoformat(), '2028-01-31')

    def test_production_and_untrusted_destinations_are_disabled_even_with_credentials(self):
        _, headers = self.account()
        for changed in ({'WEBPAY_ENV': 'production'}, {'WEBPAY_FRONTEND_URL': 'https://attacker.invalid'},
                        {'WEBPAY_RETURN_URL': 'https://api.example.invalid/wrong'}, {'WEBPAY_ENABLED': 'false'}):
            with patch.dict('os.environ', changed):
                self.assertIsNone(settings())
                self.assertFalse(self.client.get('/billing/me', headers=headers).json()['pago_habilitado'])
                self.assertEqual(self.client.post('/billing/checkout', headers=headers,
                    json={'request_id': str(uuid4())}).status_code, 503)
        self.assertEqual(self.fake.creates, 0)


class ProviderProtocolTests(unittest.TestCase):
    def test_fixed_endpoint_headers_methods_and_sanitized_failure(self):
        config = WebpaySettings('123456789012', 'x' * 64, 'https://api.example.invalid/billing/return', 'https://web.example.invalid')
        provider = WebpayProvider(config)
        with patch('app.webpay.build_opener') as factory:
            response = factory.return_value.open.return_value.__enter__.return_value
            response.read.return_value = b'{"status":"INITIALIZED"}'
            provider.status('a' * 64)
            request = factory.return_value.open.call_args.args[0]
            self.assertTrue(request.full_url.startswith('https://webpay3gint.transbank.cl/'))
            self.assertEqual(request.method, 'GET')
            self.assertEqual(request.get_header('Tbk-api-key-id'), config.commerce_code)
            factory.return_value.open.side_effect = RuntimeError('secret xxxxxxxxxx token=aaaaaaaa')
            with self.assertRaises(PaymentProviderError) as failure:
                provider.commit('a' * 64)
            self.assertNotIn('xxxxxxxxxx', str(failure.exception))
            self.assertNotIn('aaaaaaaa', str(failure.exception))
        self.assertEqual(calendar_month(datetime(2028, 1, 31)).date().isoformat(), '2028-02-29')
