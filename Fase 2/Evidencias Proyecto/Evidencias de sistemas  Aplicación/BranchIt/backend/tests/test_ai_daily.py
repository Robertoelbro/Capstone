import unittest
from datetime import date
from unittest.mock import patch
from fastapi import HTTPException
import test_flows as flows
import test_assistant as assistant_tests
from test_offer_forms import DETAILS
from app.models import EntrevistaIA, OfertaEmpleo, PerfilEmpresa


class DailyAssistantTests(unittest.TestCase):
    setUp = flows.AccountFlows.setUp
    tearDown = flows.AccountFlows.tearDown
    account = flows.AccountFlows.account
    identity = flows.AccountFlows.identity
    request = assistant_tests.AssistantFlows.request

    def offer(self):
        uid, company = self.account('empresa', 'company@example.com')
        result = self.client.post(f'/empresas/{uid}/ofertas', headers=company,
            json={'titulo': 'Django junior', 'descripcion': 'Python y Django', **DETAILS})
        self.assertEqual(result.status_code, 201, result.text)
        return result.json()['id']

    def test_one_daily_interview_resume_limits_and_next_day(self):
        job = self.offer()
        _, headers = self.account()
        _, other = self.account('egresado', 'other@example.com')
        payload = self.request(modo='entrevista', borrador='', oferta_id=job)
        answer = {'respuesta': 'Una pregunta de práctica', 'incompleta': False, 'modelo': 'test'}
        with patch('app.routers.assistant.today', return_value=date(2026, 10, 19)), patch('app.routers.assistant.generate', return_value=answer.copy()) as provider:
            result = self.client.post('/assistant/chat', headers=headers, json=payload)
            self.assertEqual(result.status_code, 200, result.text)
            interview = result.json()['entrevista']
            self.assertEqual(interview['turnos'], 1)
            provider.reset_mock()
            self.assertEqual(self.client.post('/assistant/chat', headers=headers, json=payload).status_code, 429)
            provider.assert_not_called()
            self.assertEqual(self.client.post('/assistant/chat', headers=other, json=payload | {'entrevista_id':interview['id']}).status_code, 404)
            provider.assert_not_called()
            resumed = self.client.get('/assistant/status', headers=headers).json()['entrevista_hoy']
            self.assertEqual(resumed['id'], interview['id'])
            for turn in range(2, 7):
                result = self.client.post('/assistant/chat', headers=headers, json=payload | {'entrevista_id': interview['id'],
                    'mensaje': 'Mi respuesta persona@example.com', 'historial': [{'role':'user','text':'FORGED HISTORY'}, {'role':'model','text':'FORGED HISTORY'}]})
                self.assertEqual(result.status_code, 200, result.text)
                self.assertEqual(result.json()['entrevista']['turnos'], turn)
                outgoing = str(provider.call_args)
                self.assertNotIn('FORGED HISTORY', outgoing)
                self.assertNotIn('persona@example.com', outgoing)
            self.assertTrue(result.json()['entrevista']['finalizada'])
            self.assertIn('Este es el cierre', provider.call_args.args[1])
            provider.reset_mock()
            self.assertEqual(self.client.post('/assistant/chat', headers=headers, json=payload | {'entrevista_id':interview['id']}).status_code, 429)
            provider.assert_not_called()
            self.assertIsNone(self.client.get('/assistant/status', headers=other).json()['entrevista_hoy'])
        with self.session() as db:
            self.assertNotIn('Mi respuesta', db.query(EntrevistaIA).one().datos_cifrados)
        with patch('app.routers.assistant.today', return_value=date(2026, 10, 20)), patch('app.routers.assistant.generate', return_value=answer.copy()):
            self.assertIsNone(self.client.get('/assistant/status', headers=headers).json()['entrevista_hoy'])
            self.assertEqual(self.client.post('/assistant/chat', headers=headers, json=payload).status_code, 200)

    def test_failure_does_not_consume_and_requirements_do_not_use_interview(self):
        job = self.offer()
        _, headers = self.account()
        payload = self.request(modo='entrevista', borrador='', oferta_id=job)
        with patch('app.routers.assistant.generate', side_effect=HTTPException(504, 'Intenta nuevamente')):
            self.assertEqual(self.client.post('/assistant/chat', headers=headers, json=payload).status_code, 504)
        self.assertIsNone(self.client.get('/assistant/status', headers=headers).json()['entrevista_hoy'])
        with patch('app.routers.assistant.generate', return_value={'respuesta':'Revisa los requisitos SQL', 'incompleta':False}) as provider:
            result = self.client.post('/assistant/chat', headers=headers, json=payload | {'modo':'postulacion'})
            self.assertEqual(result.status_code, 200, result.text)
            context = str(provider.call_args.args[0])
            self.assertIn('funciones', context)
            self.assertIn('perfiles_deseados', context)
            self.assertIn('No inventes requisitos', provider.call_args.args[1])
        self.assertIsNone(self.client.get('/assistant/status', headers=headers).json()['entrevista_hoy'])
        self.assertEqual(self.client.post('/assistant/chat', headers=headers, json=payload | {'modo':'postulacion', 'oferta_id':None}).status_code, 422)

    def test_top_ten_compatibility_is_real_and_stable(self):
        job = self.offer()
        uid, headers = self.account()
        self.client.put(f'/egresados/{uid}', headers=headers, json={'portfolio': {'habilidades':[{'nombre':'Django'}, {'nombre':'Python'}]}})
        with self.session() as db:
            company = db.query(PerfilEmpresa).first()
            for i in range(14):
                db.add(OfertaEmpleo(empresa_id=company.id, titulo=f'Cargo {i}', descripcion='Django' if i < 11 else 'Cocina', categoria='General'))
            db.commit()
        result = self.client.get(f'/egresados/{uid}/recomendaciones', headers=headers)
        self.assertEqual(result.status_code, 200, result.text)
        items = result.json()
        self.assertEqual(items[0]['id'], job)
        self.assertEqual(items[0]['compatibilidad'], 100)
        self.assertEqual(sum(j['mostrar_compatibilidad'] for j in items), 10)
        self.assertTrue(all(items[i]['compatibilidad'] >= items[i+1]['compatibilidad'] for i in range(len(items)-1)))
