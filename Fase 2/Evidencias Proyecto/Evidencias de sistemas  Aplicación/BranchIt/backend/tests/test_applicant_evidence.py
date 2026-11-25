import unittest
from datetime import datetime
from types import SimpleNamespace
import test_flows as flows
from test_offer_forms import DETAILS
from app.applicant_matching import affinity
from app.models import Usuario, PerfilEgresado, Postulacion, ArchivoPortfolio
from app.encryption import encrypt_data


class ApplicantEvidenceTests(unittest.TestCase):
    setUp = flows.AccountFlows.setUp
    tearDown = flows.AccountFlows.tearDown
    account = flows.AccountFlows.account
    identity = flows.AccountFlows.identity

    def test_experience_validation_snapshot_and_publication(self):
        uid, graduate = self.account()
        cid, company = self.account('empresa', 'company@example.com')
        portfolio = {'titulo_url': 'https://example.com/titulo', 'habilidades': [{'nombre': 'Django'}],
            'experiencia_laboral': [{'cargo': 'Vendedor', 'empresa': 'Cine', 'inicio': '2020-01-01', 'fin': '2021-01-01', 'descripcion': 'Atención al cliente'}]}
        for wrong in [dict(portfolio, titulo_url='javascript:alert(1)'), dict(portfolio, experiencia_laboral=[{'cargo': 'Cocinero', 'inicio': '2024-01-01', 'fin': '2020-01-01'}])]:
            self.assertEqual(self.client.put('/portfolio/me', headers=graduate, json=wrong).status_code, 422)
        saved = self.client.put(f'/egresados/{uid}', headers=graduate, json={'portfolio': portfolio})
        self.assertEqual(saved.status_code, 200, saved.text)
        job = self.client.post(f'/empresas/{cid}/ofertas', headers=company,
            json={'titulo': 'Desarrollador Django', 'descripcion': 'Python y Django', **DETAILS}).json()
        applied = self.client.post('/api/employment/applications', headers=graduate,
            json={'oferta_id': job['id'], 'formulario_version': 1, 'consentimiento': True})
        self.assertEqual(applied.status_code, 201, applied.text)
        self.assertEqual(self.client.put('/portfolio/me', headers=graduate, json={}).status_code, 200)
        url = f"/api/employment/jobs/{job['id']}/applications"
        evidence = self.client.get(url, headers=company).json()[0]
        self.assertEqual(evidence['antecedentes']['experiencia_laboral'][0]['cargo'], 'Vendedor')
        self.assertEqual(evidence['afinidad']['coincidencias'], ['Django'])
        self.assertFalse(evidence['antecedentes_actuales'])
        self.assertIsNone(evidence['portfolio_url'])
        self.client.put('/portfolio/me', headers=graduate, json=portfolio | {'publico': True})
        self.assertEqual(self.client.get(url, headers=company).json()[0]['portfolio_url'], f'/p/{uid}')
        self.assertEqual(self.client.get(f'/portfolio/{uid}').json()['portfolio']['titulo_url'], portfolio['titulo_url'])
        self.assertEqual(self.client.get(url, headers=graduate).status_code, 403)

    def test_ranking_top_ten_and_legacy_profiles(self):
        cid, company = self.account('empresa', 'company@example.com')
        other_id, other = self.account('empresa', 'other@example.com')
        job = self.client.post(f'/empresas/{cid}/ofertas', headers=company,
            json={'titulo': 'Desarrollador Django', 'descripcion': 'Python Django', **DETAILS}).json()
        with self.session() as db:
            for i in range(23):
                user = Usuario(email=f'rank{i}@example.com', password_hash='unused', tipo='egresado')
                db.add(user); db.flush()
                profile = PerfilEgresado(usuario_id=user.id, nombre='Persona', apellido=str(i), carrera='Sin definir',
                    portfolio={'habilidades': [{'nombre': n} for n in (['Django', 'Python'] if i >= 13 else ['Django'] if i >= 3 else [])]})
                db.add(profile); db.flush()
                db.add(Postulacion(oferta_id=job['id'], egresado_id=profile.id, fecha_postulacion=datetime(2026, 1, 1),
                    datos_cifrados=encrypt_data({'nombre': 'Persona', 'apellido': str(i), 'carrera': 'Sin definir'})))
            db.commit()
        url = f"/api/employment/jobs/{job['id']}/applications"
        self.assertEqual(self.client.get(url, headers=other).status_code, 404)
        result = self.client.get(url, headers=company).json()
        self.assertEqual(len(result), 23)
        self.assertEqual([x['afinidad']['puntos'] for x in result], [80]*10 + [40]*10 + [0]*3)
        self.assertEqual(sum(x['destacado'] for x in result), 10)
        self.assertEqual([x['posicion'] for x in result], list(range(1, 24)))
        self.assertTrue(all(x['antecedentes_actuales'] for x in result))
        # Exact technical boundaries and duplicate skills do not inflate points.
        fake = SimpleNamespace(titulo='Django', descripcion='', requisitos='', funciones='', perfiles_deseados=[], categoria='General')
        self.assertEqual(affinity(fake, '', {'habilidades': [{'nombre':'Go'}, {'nombre':'Django'}, {'nombre':'django'}]})['puntos'], 40)

    def test_company_photo_is_visible_but_other_files_stay_private(self):
        cid, company = self.account('empresa', 'company@example.com')
        _, graduate = self.account()
        aid = 'a' * 32
        with self.session() as db:
            db.add(ArchivoPortfolio(id=aid, usuario_id=cid, tipo='foto', nombre='logo.png', mime='image/png', tamano=10, pathname='demo/logo.png', verificado=True))
            db.commit()
        self.assertEqual(self.client.get(f'/media/{aid}/access', headers=graduate).status_code, 404)
        self.assertEqual(self.client.put(f'/empresas/{cid}/perfil', headers=company, json={'nombre_empresa':'Empresa de prueba', 'descripcion':'Empresa', 'foto_id':aid}).status_code, 200)
        self.assertEqual(self.client.get(f'/media/{aid}/access', headers=graduate).status_code, 200)
        self.assertEqual(self.client.get(f'/media/{aid}/access?remove=true', headers=graduate).status_code, 404)
        job = self.client.post(f'/empresas/{cid}/ofertas', headers=company, json={'titulo':'Cargo', 'descripcion':'Descripción', **DETAILS}).json()
        self.assertEqual(self.client.get(f"/api/employment/jobs/{job['id']}").json()['empresa_foto_id'], aid)

