import json
import unittest
import test_flows as flows
from test_offer_forms import DETAILS


class NotificationTests(unittest.TestCase):
    setUp = flows.AccountFlows.setUp
    tearDown = flows.AccountFlows.tearDown
    account = flows.AccountFlows.account
    identity = flows.AccountFlows.identity

    def test_events_private_inbox_and_read_state(self):
        company, owner = self.account('empresa', 'company@example.com')
        _, graduate = self.account()
        _, stranger = self.account('egresado', 'other@example.com')
        job = self.client.post(f'/empresas/{company}/ofertas', headers=owner,
            json={'titulo': 'Programador', 'descripcion': 'Cargo de prueba', **DETAILS}).json()
        payload = {'oferta_id': job['id'], 'formulario_version': 1, 'consentimiento': True}
        self.assertEqual(self.client.get('/notifications').status_code, 401)
        applied = self.client.post('/api/employment/applications', headers=graduate, json=payload)
        self.assertEqual(applied.status_code, 201, applied.text)
        self.assertEqual(self.client.post('/api/employment/applications', headers=graduate, json=payload).status_code, 409)
        inbox = self.client.get('/notifications', headers=owner).json()
        self.assertEqual(inbox['sin_leer'], 1)
        item = inbox['items'][0]
        self.assertEqual(item['destino'], f"/ofertas-empresa/{job['id']}/postulaciones")
        self.assertEqual(self.client.put(f"/notifications/{item['id']}/read", headers=stranger).status_code, 404)
        self.assertEqual(self.client.put(f"/notifications/{item['id']}/read", headers=owner).status_code, 204)
        self.assertEqual(self.client.get('/notifications', headers=owner).json()['sin_leer'], 0)
        close = f"/api/employment/jobs/{job['id']}/closure"
        for _ in range(2):
            self.assertEqual(self.client.put(close, headers=owner, json={'postulacion_id': applied.json()['id']}).status_code, 200)
        inbox = self.client.get('/notifications', headers=graduate).json()
        self.assertEqual(inbox['sin_leer'], 1)
        self.assertIn('se cerró', inbox['items'][0]['mensaje'])
        self.assertNotIn('seleccion', json.dumps(inbox))
        self.assertEqual(self.client.get('/notifications', headers=stranger).json()['items'], [])
        self.assertEqual(self.client.put(f"/empresas/{company}/ofertas/{job['id']}", headers=owner, json={'activa': True}).status_code, 200)
        self.assertEqual(self.client.get('/notifications', headers=graduate).json()['sin_leer'], 2)
        self.assertEqual(self.client.put('/notifications/read-all', headers=graduate).status_code, 204)
        inbox = self.client.get('/notifications', headers=graduate).json()
        self.assertEqual(inbox['sin_leer'], 0)
        self.assertEqual(len(inbox['items']), 2)
        graduate_id = self.client.get('/auth/me', headers=graduate).json()['id']
        self.assertEqual(self.client.delete(f'/egresados/{graduate_id}', headers=graduate).status_code, 204)
