import json
import unittest
from sqlalchemy.exc import IntegrityError
import test_flows as flows
from test_offer_forms import DETAILS
from app.models import Postulacion


class ClosureTests(unittest.TestCase):
    setUp = flows.AccountFlows.setUp
    tearDown = flows.AccountFlows.tearDown
    account = flows.AccountFlows.account
    identity = flows.AccountFlows.identity

    def test_owner_closes_selects_and_keeps_result_private(self):
        company, owner = self.account('empresa', 'empresa@example.com')
        other_id, other = self.account('empresa', 'otra@example.com')
        first_id, first = self.account()
        second_id, second = self.account('egresado', 'segundo@example.com')
        base = {'titulo':'Cargo', 'descripcion':'Descripción', **DETAILS}
        job = self.client.post(f'/empresas/{company}/ofertas', headers=owner, json=base).json()
        other_job = self.client.post(f'/empresas/{other_id}/ofertas', headers=other, json=base).json()
        def apply(job, headers):
            result = self.client.post('/api/employment/applications', headers=headers,
                json={'oferta_id':job['id'],'formulario_version':job['formulario_version'],'consentimiento':True})
            self.assertEqual(result.status_code,201,result.text)
            return result.json()['id']
        a, b = apply(job, first), apply(job, second)
        foreign = apply(other_job, first)
        url = f"/api/employment/jobs/{job['id']}/closure"
        self.assertEqual(self.client.put(url,json={'postulacion_id':a}).status_code,401)
        self.assertEqual(self.client.put(url,headers=first,json={'postulacion_id':a}).status_code,403)
        self.assertEqual(self.client.put(url,headers=other,json={'postulacion_id':a}).status_code,404)
        self.assertEqual(self.client.put(url,headers=owner,json={'postulacion_id':foreign}).status_code,422)
        result = self.client.put(url,headers=owner,json={'postulacion_id':a})
        self.assertEqual(result.status_code,200,result.text)
        private = self.client.get(f"/api/employment/jobs/{job['id']}/applications",headers=owner).json()
        self.assertEqual([item['id'] for item in private if item['seleccionada']],[a])
        for graduate in (first,second):
            data = self.client.get('/api/employment/applications/me',headers=graduate).json()
            own = next(item for item in data if item['oferta_id'] == job['id'])
            self.assertFalse(own['oferta_activa'])
            self.assertEqual(own['estado'],'cerrada')
            self.assertNotIn('seleccionada',json.dumps(data))
        public = self.client.get(f"/api/employment/jobs/{job['id']}").json()
        self.assertFalse(public['activa'])
        self.assertNotIn('seleccion',json.dumps(public))
        _, late = self.account('egresado','tarde@example.com')
        self.assertEqual(self.client.post('/api/employment/applications',headers=late,json={'oferta_id':job['id'],'formulario_version':1,'consentimiento':True}).status_code,409)
        with self.session() as db:
            db.get(Postulacion,b).seleccionada=True
            with self.assertRaises(IntegrityError):
                db.commit()
            db.rollback()
        self.assertEqual(self.client.put(url,headers=owner,json={'postulacion_id':b}).status_code,200)
        private = self.client.get(f"/api/employment/jobs/{job['id']}/applications",headers=owner).json()
        self.assertEqual([item['id'] for item in private if item['seleccionada']],[b])
        self.assertEqual(self.client.put(f"/empresas/{company}/ofertas/{job['id']}",headers=owner,json={'activa':True}).status_code,200)
        private = self.client.get(f"/api/employment/jobs/{job['id']}/applications",headers=owner).json()
        self.assertFalse(any(item['seleccionada'] for item in private))
        self.assertEqual(self.client.put(url,headers=owner,json={'postulacion_id':None}).status_code,200)
