import unittest
from unittest.mock import patch
from urllib.parse import urlsplit
import test_flows as flows
import test_assistant as assistant_tests
from test_offer_forms import DETAILS
from app.certifications import CATALOG, recommend_certifications


class CertificationTests(unittest.TestCase):
    setUp = flows.AccountFlows.setUp
    tearDown = flows.AccountFlows.tearDown
    account = flows.AccountFlows.account
    identity = flows.AccountFlows.identity
    request = assistant_tests.AssistantFlows.request

    def test_catalog_relevance_and_scope(self):
        self.assertEqual(recommend_certifications('Python Django SQL')[0]['nombre'], 'freeCodeCamp')
        self.assertEqual(recommend_certifications('Marketing ventas finanzas')[0]['nombre'], 'HP LIFE')
        resources = recommend_certifications('Enfermería pediátrica')
        self.assertTrue(all('transversales' in r['motivo'] or 'complemento' in r['motivo'] for r in resources))
        for resource in CATALOG:
            self.assertEqual(urlsplit(resource['url']).scheme, 'https')
            self.assertIn(urlsplit(resource['url']).hostname, {'www.freecodecamp.org', 'skillsbuild.org', 'www.life-global.org'})

    def test_requirements_get_official_links_without_model_urls(self):
        company, owner = self.account('empresa', 'company@example.com')
        _, graduate = self.account()
        job = self.client.post(f'/empresas/{company}/ofertas', headers=owner,
            json={'titulo':'Desarrollador Python', 'descripcion':'Python y SQL', **DETAILS}).json()
        with patch('app.routers.assistant.generate', return_value={'respuesta':'Busca recursos de Python.', 'incompleta':False}) as provider:
            response = self.client.post('/assistant/chat', headers=graduate,
                json=self.request(modo='postulacion', oferta_id=job['id'], borrador='', mensaje='¿Dónde puedo certificarme gratis?'))
            self.assertEqual(response.status_code, 200, response.text)
            resources = response.json()['recursos_certificacion']
            self.assertLessEqual(len(resources), 3)
            self.assertEqual(resources[0]['nombre'], 'freeCodeCamp')
            self.assertIn('sitios_formacion_verificados', str(provider.call_args.args[0]))
            self.assertIn('No inventes cursos', provider.call_args.args[1])
            self.assertIn('certificado de finalización', provider.call_args.args[1])
        self.assertIsNone(self.client.get('/assistant/status', headers=graduate).json()['entrevista_hoy'])

    def test_request_in_review_mode_and_resume_keeps_links(self):
        company, owner = self.account('empresa', 'company@example.com')
        _, graduate = self.account()
        job = self.client.post(f'/empresas/{company}/ofertas', headers=owner,
            json={'titulo':'Marketing', 'descripcion':'Ventas', **DETAILS}).json()
        answer = {'respuesta':'HP LIFE tiene formación en negocios.', 'incompleta':False}
        with patch('app.routers.assistant.generate', return_value=answer):
            response = self.client.post('/assistant/chat', headers=graduate,
                json=self.request(mensaje='Recomiéndame cursos de marketing con certificado'))
            self.assertEqual(response.status_code, 200, response.text)
            self.assertEqual(response.json()['recursos_certificacion'][0]['nombre'], 'HP LIFE')
            response = self.client.post('/assistant/chat', headers=graduate,
                json=self.request(modo='entrevista', oferta_id=job['id'], mensaje='Recomiéndame certificaciones de ventas'))
            self.assertEqual(response.status_code, 200, response.text)
            state = self.client.get('/assistant/status', headers=graduate).json()['entrevista_hoy']
            self.assertEqual(state['historial'][-1]['recursos'][0]['nombre'], 'HP LIFE')
            response = self.client.post('/assistant/chat', headers=graduate,
                json=self.request(modo='entrevista', oferta_id=job['id'], entrevista_id=state['id'], mensaje='Continuemos'))
            self.assertEqual(response.status_code, 200, response.text)
