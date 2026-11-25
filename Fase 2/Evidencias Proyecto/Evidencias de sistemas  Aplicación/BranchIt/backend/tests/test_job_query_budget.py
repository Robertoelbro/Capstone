"""Offer list query budgets must not grow with the number of companies."""
import unittest
from sqlalchemy import event

import test_flows as flows
from app.models import ArchivoPortfolio, OfertaEmpleo, PerfilEmpresa, TipoUsuario, Usuario


class JobQueryBudgetTests(unittest.TestCase):
    setUp = flows.AccountFlows.setUp
    tearDown = flows.AccountFlows.tearDown
    account = flows.AccountFlows.account
    identity = flows.AccountFlows.identity

    def add_companies(self, start, amount, active=True):
        expected = {}
        with self.session() as db:
            for index in range(start, start + amount):
                company = Usuario(email=f'private-owner-{index}@example.com', password_hash='not-for-login',
                    tipo=TipoUsuario.empresa, activo=active)
                db.add(company)
                db.flush()
                photo_id = f'{index + 1:032x}'
                db.add(ArchivoPortfolio(id=photo_id, usuario_id=company.id, tipo='foto', nombre='Foto demo',
                    mime='image/png', tamano=100, pathname=f'query-budget/{photo_id}.png', verificado=True))
                db.flush()
                profile = PerfilEmpresa(usuario_id=company.id, nombre_empresa=f'Empresa {index}',
                    foto_id=photo_id, logo_url=f'https://example.invalid/logo-{index}.png')
                db.add(profile)
                db.flush()
                for position in range(10):
                    job = OfertaEmpleo(empresa_id=profile.id, titulo=f'Cargo {index}-{position}',
                        descripcion='Desarrollo Django', requisitos='Django', activa=True)
                    db.add(job)
                    db.flush()
                    expected[job.id] = (profile.nombre_empresa, photo_id, profile.logo_url)
            db.commit()
        return expected

    def read_counted(self, path, headers):
        selects = []
        def capture(conn, cursor, statement, parameters, context, executemany):
            if statement.lstrip().upper().startswith('SELECT'):
                selects.append(1)
        event.listen(self.engine, 'before_cursor_execute', capture)
        try:
            response = self.client.get(path, headers=headers)
        finally:
            event.remove(self.engine, 'before_cursor_execute', capture)
        self.assertEqual(response.status_code, 200, response.text)
        return response.json(), len(selects)

    def test_query_count_constant_from_one_to_ten_companies_and_media_preserved(self):
        graduate, headers = self.account()
        paths = [('/api/employment/jobs', {}, 1),
                 (f'/egresados/{graduate}/ofertas', headers, 3),
                 (f'/egresados/{graduate}/recomendaciones', headers, 3)]
        expected = self.add_companies(0, 1)
        baseline = {}
        for path, auth, budget in paths:
            body, count = self.read_counted(path, auth)
            self.assertEqual(len(body), 10)
            self.assertLessEqual(count, budget)
            baseline[path] = count
        expected.update(self.add_companies(1, 9))
        self.add_companies(10, 1, active=False)
        for path, auth, budget in paths:
            body, count = self.read_counted(path, auth)
            self.assertEqual(len(body), 100)
            self.assertEqual(count, baseline[path])
            self.assertLessEqual(count, budget)
            self.assertEqual({item['id'] for item in body}, set(expected))
            for item in body:
                self.assertEqual((item['nombre_empresa'], item['empresa_foto_id'], item['empresa_logo_url']), expected[item['id']])
                self.assertNotIn('password_hash', item)
                self.assertNotIn('email', item)
            if path.endswith('/recomendaciones'):
                self.assertTrue(all('compatibilidad' in item and 'coincidencias' in item for item in body))
            else:
                self.assertEqual([row['fecha_publicacion'] for row in body],
                    sorted([row['fecha_publicacion'] for row in body], reverse=True))
