import unittest
import test_flows as flows
from app.models import OfertaEmpleo


DETAILS = {'sueldo': 850000, 'funciones': 'Desarrollar interfaces accesibles.',
           'perfiles_deseados': ['Ingeniería en Informática'],
           'condiciones_laborales': 'Jornada completa. Contrato indefinido.',
           'adaptada_discapacidad': True}


class OfferForms(unittest.TestCase):
    setUp = flows.AccountFlows.setUp
    tearDown = flows.AccountFlows.tearDown
    account = flows.AccountFlows.account
    identity = flows.AccountFlows.identity

    def test_required_details_salary_validation_and_legacy_read(self):
        company, headers = self.account('empresa', 'empresa@example.com')
        url = f'/empresas/{company}/ofertas'
        payload = {'titulo': 'Cargo', 'descripcion': 'Descripción', **DETAILS}
        for name in DETAILS:
            missing = {k: v for k, v in payload.items() if k != name}
            self.assertEqual(self.client.post(url, headers=headers, json=missing).status_code, 422, name)
        for invalid in ({'sueldo':0}, {'sueldo':-1}, {'sueldo':1.5}, {'sueldo':'850.000'},
                        {'funciones':' '}, {'condiciones_laborales':' '}, {'perfiles_deseados':[]},
                        {'perfiles_deseados':[' ']}, {'perfiles_deseados':['A','a']}):
            self.assertEqual(self.client.post(url, headers=headers, json=payload | invalid).status_code, 422, invalid)
        result = self.client.post(url, headers=headers, json=payload)
        self.assertEqual(result.status_code, 201, result.text)
        job = result.json()['id']
        self.assertEqual(self.client.get(f'/api/employment/jobs/{job}').json()['sueldo'],850000)
        graduate_id, graduate = self.account()
        suggested = self.client.get(f'/egresados/{graduate_id}/recomendaciones', headers=graduate).json()
        self.assertTrue(next(item for item in suggested if item['id'] == job)['afin'])
        self.assertEqual(self.client.put(f'{url}/{job}',headers=headers,json={'sueldo':None}).status_code,422)
        with self.session() as db:
            item = db.get(OfertaEmpleo,job)
            for name in DETAILS:
                setattr(item,name,None)
            db.commit()
        self.assertIsNone(self.client.get(f'/api/employment/jobs/{job}').json()['sueldo'])
        self.assertEqual(self.client.put(f'{url}/{job}',headers=headers,json={'titulo':'Nuevo'}).status_code,422)
        self.assertEqual(self.client.put(f'{url}/{job}',headers=headers,json={'activa':False}).status_code,200)
        self.assertEqual(self.client.put(f'{url}/{job}',headers=headers,json=DETAILS).status_code,200)

    def test_multiple_choice_and_character_limits_are_validated_and_preserved(self):
        company, headers = self.account('empresa','empresa@example.com')
        questions = [{'id':'m','etiqueta':'Herramientas','tipo':'seleccion_multiple','opciones':['Python','Git'],'obligatoria':True},
                     {'id':'s','etiqueta':'Resumen','tipo':'texto','obligatoria':True},
                     {'id':'l','etiqueta':'Detalle','tipo':'parrafo','obligatoria':False},
                     {'id':'n','etiqueta':'Número','tipo':'numero','obligatoria':True}]
        result = self.client.post(f'/empresas/{company}/ofertas',headers=headers,json={**DETAILS,'titulo':'Cargo','descripcion':'Descripción','preguntas':questions})
        self.assertEqual(result.status_code,201,result.text)
        job = result.json()
        _, graduate = self.account()
        payload = {'oferta_id':job['id'],'formulario_version':job['formulario_version'],'consentimiento':True,
                   'respuestas':{'m':['Python','Git'],'s':'x'*200,'l':'x'*3000,'n':'12,5'}}
        for invalid in ({'m':[]},{'m':['Python','Python']},{'m':['Otro']},{'m':'Python'},
                        {'s':['texto']},{'s':'x'*201},{'l':'x'*3001},{'n':'1e3'},{'n':'NaN'}):
            response=self.client.post('/api/employment/applications',headers=graduate,json=payload | {'respuestas':payload['respuestas'] | invalid})
            self.assertEqual(response.status_code,422,response.text)
        result = self.client.post('/api/employment/applications',headers=graduate,json=payload)
        self.assertEqual(result.status_code,201,result.text)
        saved=self.client.get(f"/api/employment/jobs/{job['id']}/applications",headers=headers).json()[0]
        self.assertEqual(saved['datos']['respuestas']['m'],['Python','Git'])
        self.assertEqual(saved['datos']['preguntas'][0]['tipo'],'seleccion_multiple')
