"""Safety boundaries of the optional remote QA harness; never open sockets."""
import unittest
import httpx

from scripts.load_preview import run, validate_manifest


class QualityLoadTests(unittest.TestCase):
    def manifest(self):
        return {'origin': 'https://branchit-api-abc123456-team.vercel.app', 'target': 'preview',
                'database': 'postgresql_isolated', 'qa_run_id': 'a' * 32,
                'graduate_id': 1, 'expected_offers': 100}

    def test_forbidden_destinations_and_manifest_cannot_bypass_allowlist(self):
        for origin in ('https://branchit-api.vercel.app', 'https://branchit-blue.vercel.app',
                       'https://example.com', 'http://branchit-api-abc123456-team.vercel.app',
                       'https://user:password@branchit-api-abc123456-team.vercel.app',
                       'https://branchit-api-abc123456-team.vercel.app/private',
                       'https://branchit-api-abc123456-team.vercel.app?token=secret'):
            with self.assertRaises(ValueError):
                validate_manifest(self.manifest() | {'origin': origin})
        with self.assertRaises(ValueError):
            validate_manifest(self.manifest() | {'database': 'production'})
        with self.assertRaises(ValueError):
            validate_manifest(self.manifest() | {'target': 'production'})

    def test_only_explicit_project_qa_alias_is_allowed(self):
        origin = 'https://branchit-qa-api-roberto-el-bro.vercel.app'
        self.assertEqual(validate_manifest(self.manifest() | {'origin': origin}), origin)
        with self.assertRaises(ValueError):
            validate_manifest(self.manifest() | {'origin': 'https://other-qa-api-team.vercel.app'})

    def test_no_graduate_token_sent_before_server_attestation(self):
        captured = []
        def server(request):
            captured.append(request)
            return httpx.Response(200, json={'status': 'ok'})
        with self.assertRaises(ValueError):
            run(self.manifest(), 'private-test-token', transport=httpx.MockTransport(server))
        self.assertEqual(len(captured), 1)
        self.assertNotIn('authorization', captured[0].headers)
        self.assertEqual(captured[0].url.path, '/health/ready')

    def test_redirect_does_not_send_token_to_another_host(self):
        captured = []
        def server(request):
            captured.append(request)
            return httpx.Response(307, headers={'location': 'https://example.com/'})
        with self.assertRaises(ValueError):
            run(self.manifest(), 'private-test-token', transport=httpx.MockTransport(server))
        self.assertEqual(len(captured), 1)
        self.assertNotIn('authorization', captured[0].headers)

    def test_fixture_mismatch_aborts_before_load(self):
        captured = []
        def server(request):
            captured.append(request)
            if request.url.path == '/health/ready':
                return httpx.Response(200, headers={'X-BranchIT-QA-Run': 'a' * 32}, json={'status': 'ok'})
            return httpx.Response(200, json=[])
        with self.assertRaises(ValueError):
            run(self.manifest(), 'private-test-token', transport=httpx.MockTransport(server))
        self.assertEqual(len(captured), 2)
        self.assertTrue(all(request.url.path not in ('/billing/checkout', '/assistant/chat') for request in captured))

    def test_limits_reject_excessive_budget_before_network(self):
        def forbidden(_):
            self.fail('No debe abrir una solicitud con presupuesto inválido.')
        for kwargs in ({'requests': 301}, {'concurrencies': [11]}, {'timeout': 11}, {'max_rps': 11}):
            with self.assertRaises(ValueError):
                run(self.manifest(), 'private-test-token', transport=httpx.MockTransport(forbidden), **kwargs)

    def test_first_load_error_stops_and_report_never_contains_token_or_origin(self):
        captured = []
        def server(request):
            captured.append(request.url.path)
            if request.url.path == '/health/ready':
                return httpx.Response(200, headers={'X-BranchIT-QA-Run': 'a' * 32}, json={'status': 'ok'})
            if len(captured) > 4:
                return httpx.Response(503, json={'detail': 'fallo simulado'})
            body = {'id': 1, 'tipo': 'egresado'} if request.url.path == '/auth/me' else [{}] * 100
            return httpx.Response(200, json=body)
        report = run(self.manifest(), 'private-test-token', requests=10, concurrencies=[1, 5],
                     transport=httpx.MockTransport(server))
        self.assertEqual(len(report['scenarios']), 1)
        self.assertEqual(report['scenarios'][0]['requests'], 1)
        self.assertEqual(report['scenarios'][0]['errors'], 1)
        self.assertFalse(report['scenarios'][0]['completed'])
        self.assertNotIn('private-test-token', str(report))
        self.assertNotIn(self.manifest()['origin'], str(report))
        self.assertEqual(len(captured), 5)

    def test_transport_error_reports_only_permitted_class_not_message_or_url(self):
        captured = []
        def server(request):
            captured.append(request.url.path)
            if request.url.path == '/health/ready':
                return httpx.Response(200, headers={'X-BranchIT-QA-Run': 'a' * 32}, json={'status': 'ok'})
            if len(captured) > 4:
                raise httpx.ReadTimeout('hidden-message-token https://private.invalid/?secret=hidden',
                                        request=request)
            body = {'id': 1, 'tipo': 'egresado'} if request.url.path == '/auth/me' else [{}] * 100
            return httpx.Response(200, json=body)
        report = run(self.manifest(), 'private-test-token', requests=10, concurrencies=[1],
                     transport=httpx.MockTransport(server))
        scenario = report['scenarios'][0]
        self.assertEqual(scenario['transport_errors'], {'ReadTimeout': 1})
        self.assertEqual(scenario['routes']['jobs']['transport_errors'], {'ReadTimeout': 1})
        self.assertEqual(scenario['requests'], 1)
        self.assertFalse(scenario['completed'])
        for private in ('hidden-message-token', 'private.invalid', 'secret=hidden',
                        'private-test-token', self.manifest()['origin']):
            self.assertNotIn(private, str(report))
