"""Sprint 9: adversarial boundaries, without production services or model calls."""
import asyncio
import unittest
from unittest.mock import Mock

import test_flows as flows
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError
from app.main import app
from app.database import get_db
from app.config import CORS_ORIGINS
from app.request_guard import RequestGuard


class RequestBoundaryTests(unittest.TestCase):
    def request(self, chunks, headers=None):
        messages, called = [], []
        queue = [{'type': 'http.request', 'body': body, 'more_body': i < len(chunks) - 1}
                 for i, body in enumerate(chunks)]

        async def receive():
            return queue.pop(0)

        async def send(message):
            messages.append(message)

        async def endpoint(scope, receive, send):
            called.append(await receive())
            await send({'type': 'http.response.start', 'status': 204, 'headers': []})
            await send({'type': 'http.response.body', 'body': b''})

        scope = {'type': 'http', 'method': 'POST', 'headers': headers or []}
        asyncio.run(RequestGuard(endpoint, max_bytes=10)(scope, receive, send))
        return messages, called

    def test_chunked_limit_cannot_be_bypassed_with_small_content_length(self):
        messages, called = self.request([b'12345', b'678901'], [(b'content-length', b'5')])
        self.assertEqual(messages[0]['status'], 413)
        self.assertFalse(called)
        self.assertIn((b'cache-control', b'no-store'), messages[0]['headers'])

    def test_declared_oversize_rejected_before_body_is_read(self):
        messages, called = self.request([], [(b'content-length', b'11')])
        self.assertEqual(messages[0]['status'], 413)
        self.assertFalse(called)

    def test_invalid_or_ambiguous_length_is_rejected(self):
        for headers in [[(b'content-length', b'-1')], [(b'content-length', b'9' * 5000)],
                        [(b'content-length', b'1'), (b'content-length', b'2')]]:
            messages, called = self.request([], headers)
            self.assertEqual(messages[0]['status'], 400)
            self.assertFalse(called)

    def test_small_chunked_request_reaches_endpoint_intact(self):
        messages, called = self.request([b'123', b'4567'])
        self.assertEqual(messages[0]['status'], 204)
        self.assertEqual(called[0]['body'], b'1234567')


class SecurityResponseTests(unittest.TestCase):
    setUp = flows.AccountFlows.setUp
    tearDown = flows.AccountFlows.tearDown

    def test_health_checks_database_without_exposing_configuration(self):
        self.assertEqual(self.client.get('/health').json(), {'estado': 'ok'})
        self.assertEqual(self.client.get('/health/ready').json(), {'estado': 'listo'})

    def test_database_failure_does_not_disclose_sql_or_credentials(self):
        failing = Mock()
        failing.execute.side_effect = OperationalError('SELECT secret_table', {'password': 'private-value'}, Exception('private-host'))
        app.dependency_overrides[get_db] = lambda: failing
        response = self.client.get('/health/ready')
        self.assertEqual(response.status_code, 503)
        for value in ['secret_table', 'private-value', 'private-host']:
            self.assertNotIn(value, response.text)
        self.assertEqual(response.headers['cache-control'], 'no-store')

    def test_unexpected_failure_has_generic_message_and_headers(self):
        failing = Mock()
        failing.execute.side_effect = RuntimeError('private-database-connection')
        app.dependency_overrides[get_db] = lambda: failing
        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.get('/health/ready')
        self.assertEqual(response.status_code, 500)
        self.assertNotIn('private-database-connection', response.text)
        self.assertEqual(response.headers['x-content-type-options'], 'nosniff')

    def test_validation_and_authentication_do_not_echo_secrets(self):
        response = self.client.post('/auth/login', json={'email': 'invalid-private-email', 'password': 'private-password'})
        self.assertEqual(response.status_code, 422)
        self.assertNotIn('invalid-private-email', response.text)
        self.assertNotIn('private-password', response.text)
        response = self.client.get('/auth/me', headers={'Authorization': 'Bearer forged-token'})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.headers['www-authenticate'], 'Bearer')
        self.assertEqual(response.headers['cache-control'], 'no-store')

    def test_cors_only_allows_configured_origins(self):
        headers = {'Origin': CORS_ORIGINS[0], 'Access-Control-Request-Method': 'POST'}
        allowed = self.client.options('/auth/login', headers=headers)
        self.assertEqual(allowed.status_code, 200)
        self.assertEqual(allowed.headers['access-control-allow-origin'], CORS_ORIGINS[0])
        denied = self.client.options('/auth/login', headers={**headers, 'Origin': 'https://untrusted.invalid'})
        self.assertEqual(denied.status_code, 400)
        self.assertNotIn('access-control-allow-origin', denied.headers)
