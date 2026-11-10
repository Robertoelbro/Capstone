"""Recruiter hiring, private PDF release and the permanent one-employment year limit."""
import unittest
from datetime import date
from unittest.mock import patch
from uuid import uuid4

import test_flows as flows
from test_offer_forms import DETAILS
from app.encryption import decrypt_data, encrypt_data
from app.models import ArchivoPortfolio, SeguimientoLaboral
from app.routers.career import anniversary


class HiringReleaseTests(unittest.TestCase):
    setUp = flows.AccountFlows.setUp
    tearDown = flows.AccountFlows.tearDown
    account = flows.AccountFlows.account
    identity = flows.AccountFlows.identity

    def job(self, company, headers):
        r = self.client.post(f'/empresas/{company}/ofertas', headers=headers,
            json={'titulo': 'Cargo de prueba', 'descripcion': 'Primer empleo', **DETAILS})
        self.assertEqual(r.status_code, 201, r.text)
        return r.json()

    def apply(self, job, headers):
        return self.client.post('/api/employment/applications', headers=headers,
            json={'oferta_id': job['id'], 'formulario_version': job['formulario_version'], 'consentimiento': True})

    def asset(self, user_id, **changes):
        asset_id = uuid4().hex
        with self.session() as db:
            db.add(ArchivoPortfolio(**{'id': asset_id, 'usuario_id': user_id, 'tipo': 'finiquito',
                'nombre': 'privado.pdf', 'mime': 'application/pdf', 'tamano': 150,
                'verificado': True, 'pathname': f'test/{asset_id}.pdf', **changes}))
            db.commit()
        return asset_id

    def start(self, headers, start='2025-01-01'):
        result = self.client.put('/employment/me', headers=headers,
            json={'situacion': 'trabajando', 'busqueda_activa': True, 'fecha_inicio': start})
        self.assertEqual(result.status_code, 200, result.text)
        return result.json()

    def release(self, headers, asset, end, **extra):
        return self.client.post('/employment/release', headers=headers,
            json={'archivo_id': asset, 'fecha_fin': end, 'motivo': 'renuncia', **extra})

    def test_selected_candidate_is_hired_other_candidates_remain_private(self):
        company, owner = self.account('empresa', 'company@example.com')
        first_id, first = self.account()
        _, second = self.account('egresado', 'second@example.com')
        job = self.job(company, owner)
        another = self.job(company, owner)
        a = self.apply(job, first).json()['id']
        self.apply(job, second)
        result = self.client.put(f"/api/employment/jobs/{job['id']}/closure", headers=owner,
            json={'postulacion_id': a, 'fecha_inicio': '2026-01-01'})
        self.assertEqual(result.status_code, 200, result.text)
        status = self.client.get('/employment/me', headers=first).json()
        self.assertEqual((status['situacion'], status['fecha_inicio'], status['origen']), ('trabajando', '2026-01-01', 'empresa'))
        self.assertFalse(status['puede_postular'])
        self.assertTrue(status['requiere_finiquito'])
        self.assertTrue(self.client.get('/employment/me', headers=second).json()['puede_postular'])
        self.assertEqual(self.apply(another, first).status_code, 409)
        self.assertEqual(self.client.put('/employment/me', headers=first,
            json={'situacion': 'buscando', 'busqueda_activa': True}).status_code, 409)
        public_history = self.client.get('/api/employment/applications/me', headers=second).text
        self.assertNotIn('seleccionada', public_history)
        self.assertNotIn('fecha_inicio_contratacion', public_history)
        private = self.client.get(f"/api/employment/jobs/{job['id']}/applications", headers=owner).json()
        self.assertEqual(next(i for i in private if i['id'] == a)['fecha_inicio_contratacion'], '2026-01-01')
        # Reopening and closing again must not clear or rewrite the original hire date.
        self.assertEqual(self.client.put(f"/empresas/{company}/ofertas/{job['id']}", headers=owner, json={'activa': True}).status_code, 200)
        self.client.put(f"/api/employment/jobs/{job['id']}/closure", headers=owner,
            json={'postulacion_id': a, 'fecha_inicio': '2026-02-01'})
        self.assertEqual(self.client.get('/employment/me', headers=first).json()['fecha_inicio'], '2026-01-01')
        pdf = self.asset(first_id)
        self.assertEqual(self.release(first, pdf, '2026-02-01').status_code, 200)
        self.client.put(f"/api/employment/jobs/{job['id']}/closure", headers=owner, json={'postulacion_id': a})
        self.assertTrue(self.client.get('/employment/me', headers=first).json()['puede_postular'])

    def test_exact_year_permanent_gate_survives_updates_and_new_declared_employment(self):
        user_id, headers = self.account()
        self.start(headers)
        pdf = self.asset(user_id)
        result = self.release(headers, pdf, '2026-01-01')
        self.assertEqual(result.status_code, 200, result.text)
        self.assertTrue(result.json()['limite_experiencia'])
        self.assertFalse(result.json()['puede_postular'])
        self.assertEqual(result.json()['motivo_bloqueo'], 'limite_experiencia')
        self.assertEqual(self.client.put('/employment/me', headers=headers,
            json={'situacion': 'buscando', 'busqueda_activa': True}).status_code, 409)
        self.start(headers, '2026-02-01')
        second = self.asset(user_id)
        again = self.release(headers, second, '2026-03-01')
        self.assertTrue(again.json()['limite_experiencia'])
        self.assertFalse(again.json()['puede_postular'])
        company, owner = self.account('empresa', 'company@example.com')
        self.assertEqual(self.apply(self.job(company, owner), headers).status_code, 409)
        self.assertEqual(self.client.get('/auth/me', headers=headers).status_code, 200)

    def test_second_company_cannot_replace_current_employment_or_change_other_selection(self):
        company, owner = self.account('empresa', 'first-company@example.com')
        another_company, other = self.account('empresa', 'other-company@example.com')
        _, graduate = self.account()
        _, second = self.account('egresado', 'second@example.com')
        first_job, second_job = self.job(company, owner), self.job(another_company, other)
        first_application = self.apply(first_job, graduate).json()['id']
        another_application = self.apply(second_job, graduate).json()['id']
        second_application = self.apply(first_job, second).json()['id']
        self.assertEqual(self.client.put(f"/api/employment/jobs/{first_job['id']}/closure", headers=owner,
            json={'postulacion_id': first_application, 'fecha_inicio': '2026-01-01'}).status_code, 200)
        result = self.client.put(f"/api/employment/jobs/{second_job['id']}/closure", headers=other,
            json={'postulacion_id': another_application, 'fecha_inicio': '2026-02-01'})
        self.assertEqual(result.status_code, 409, result.text)
        self.assertTrue(self.client.get(f"/api/employment/jobs/{second_job['id']}").json()['activa'])
        self.assertEqual(self.client.get('/employment/me', headers=graduate).json()['fecha_inicio'], '2026-01-01')
        # Selecting another finalist does not erase the first graduate's employment.
        self.assertEqual(self.client.put(f"/api/employment/jobs/{first_job['id']}/closure", headers=owner,
            json={'postulacion_id': second_application, 'fecha_inicio': '2026-02-01'}).status_code, 200)
        self.assertFalse(self.client.get('/employment/me', headers=graduate).json()['puede_postular'])
        self.assertFalse(self.client.get('/employment/me', headers=second).json()['puede_postular'])

    def test_under_year_releases_but_pdf_stays_private_and_undeletable(self):
        user_id, headers = self.account()
        _, other = self.account('egresado', 'other@example.com')
        self.start(headers)
        pdf = self.asset(user_id)
        result = self.release(headers, pdf, '2025-12-31')
        self.assertEqual(result.status_code, 200, result.text)
        self.assertTrue(result.json()['puede_postular'])
        self.assertFalse(result.json()['limite_experiencia'])
        self.assertEqual(self.client.get(f'/media/{pdf}/access', headers=headers).status_code, 200)
        self.assertEqual(self.client.get(f'/media/{pdf}/access').status_code, 404)
        self.assertEqual(self.client.get(f'/media/{pdf}/access', headers=other).status_code, 404)
        self.assertEqual(self.client.get(f'/media/{pdf}/access?remove=true', headers=headers).status_code, 409)
        self.assertEqual(self.client.get(f'/media/{pdf}/access?upload=true', headers=headers).status_code, 409)
        with patch.dict('os.environ', {'MEDIA_SERVICE_SECRET': 'test-media-secret'}):
            self.assertEqual(self.client.delete(f'/media/{pdf}', headers={**headers, 'X-Media-Service': 'test-media-secret'}).status_code, 409)
        self.client.put('/employment/me', headers=headers, json={'situacion': 'buscando', 'busqueda_activa': False})
        self.start(headers, '2026-01-01')
        self.assertEqual(self.release(headers, pdf, '2026-02-01').status_code, 409)
        with self.session() as db:
            row = db.query(SeguimientoLaboral).filter_by(usuario_id=user_id).one()
            self.assertNotIn(pdf, row.datos_cifrados)
            self.assertEqual(len(decrypt_data(row.datos_cifrados)['historial_empleos']), 1)

    def test_only_owned_verified_finiquito_and_unchanged_dates_are_accepted(self):
        user_id, headers = self.account()
        other_id, _ = self.account('egresado', 'other@example.com')
        self.start(headers)
        for asset in (self.asset(other_id), self.asset(user_id, verificado=False),
                      self.asset(user_id, tipo='certificado'), self.asset(user_id, tamano=6 * 1024 * 1024)):
            self.assertEqual(self.release(headers, asset, '2025-02-01').status_code, 422)
        pdf = self.asset(user_id)
        self.assertEqual(self.release(headers, pdf, '2025-02-01', fecha_inicio='2025-01-02').status_code, 422)
        self.assertEqual(self.release(headers, pdf, '2024-12-31').status_code, 422)
        self.assertEqual(self.release(headers, pdf, '2099-01-01').status_code, 422)
        self.assertEqual(self.client.post('/employment/release', json={'archivo_id': pdf, 'fecha_fin': '2025-01-02', 'motivo': 'renuncia'}).status_code, 401)
        company, owner = self.account('empresa', 'company@example.com')
        self.assertEqual(self.release(owner, pdf, '2025-02-01').status_code, 403)

    def test_pdf_reservation_limits_and_legacy_start_correction(self):
        user_id, headers = self.account()
        base = {'tipo': 'finiquito', 'nombre': 'documento.pdf', 'mime': 'application/pdf', 'tamano': 100}
        self.assertEqual(self.client.post('/media/reserve', headers=headers, json=base).status_code, 201)
        self.assertEqual(self.client.post('/media/reserve', headers=headers, json=base | {'mime': 'image/png'}).status_code, 422)
        self.assertEqual(self.client.post('/media/reserve', headers=headers, json=base | {'tamano': 5 * 1024 * 1024 + 1}).status_code, 422)
        with self.session() as db:
            db.add(SeguimientoLaboral(usuario_id=user_id, situacion='trabajando', busqueda_activa=False,
                datos_cifrados=encrypt_data({'fecha_inicio': None}), limite_experiencia=False))
            db.commit()
        pdf = self.asset(user_id)
        self.assertEqual(self.release(headers, pdf, '2025-02-01').status_code, 422)
        result = self.release(headers, pdf, '2025-02-01', fecha_inicio='2025-01-01')
        self.assertEqual(result.status_code, 200, result.text)
        self.assertTrue(result.json()['puede_postular'])
        self.assertEqual(anniversary(date(2024, 2, 29)), date(2025, 2, 28))
