import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from sqlalchemy import text
import test_flows as flows
from app.models import Usuario, PerfilEmpresa, PerfilEgresado, OfertaEmpleo, Postulacion, ArchivoPortfolio
from app.schemas import RegistroEmpresa, OfertaEmpleoCreate
from app.careers import career_area
from scripts.seed_jobs import seed, jobs, company_accounts, reset_companies, graduate_snapshot, reset_sql, SCHEMA_VERSION
from test_offer_forms import DETAILS


class SeedResetTests(unittest.TestCase):
    setUp = flows.AccountFlows.setUp
    tearDown = flows.AccountFlows.tearDown
    account = flows.AccountFlows.account
    identity = flows.AccountFlows.identity

    def version(self, db):
        db.execute(text('CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL)'))
        db.execute(text('INSERT INTO alembic_version VALUES (:version)'), {'version':SCHEMA_VERSION})
        db.commit()

    def test_current_demo_data_validates_like_real_registration_and_offer_creation(self):
        values = jobs()
        self.assertEqual(len(values),100)
        self.assertEqual(len({j['demo_clave'] for j in values}),100)
        self.assertEqual({j['modalidad'] for j in values},{'presencial','remoto','hibrido'})
        self.assertEqual({q['tipo'] for j in values for q in j['preguntas']},{'texto','parrafo','numero','seleccion','seleccion_multiple'})
        for job in values:
            OfertaEmpleoCreate.model_validate({k:v for k,v in job.items() if k not in ('empresa','demo_clave')})
            for career in job['perfiles_deseados']:
                self.assertEqual(career_area(career),job['categoria'],career)
        for item in company_accounts():
            RegistroEmpresa.model_validate({'email':item['correo'],'password':item['contraseña'],
                'nombre_empresa':item['empresa'],'rubro':item['giro'],'rut':item['rut'],'telefono':item['telefono'],'fecha_identidad':item['fecha_identidad']})
        sql = reset_sql('branchit_backup_test',{'empresas':13,'postulaciones':3})
        self.assertIn('CREATE SCHEMA branchit_backup_test',sql)
        self.assertIn('graduates_before IS DISTINCT FROM graduates_after',sql)
        self.assertEqual(sql.count('INSERT INTO ofertas_empleo'),100)
        self.assertEqual(sql.count('INSERT INTO usuarios'),10)
        self.assertNotIn('TRUNCATE',sql)
        self.assertIn("Cambió la cantidad de empresas",sql)
        with self.assertRaises(ValueError):
            reset_sql('branchit_backup_test',{'empresas':"13;DELETE"})

    def test_reset_backs_up_all_companies_and_preserves_graduate_data_and_files(self):
        graduate, headers = self.account()
        with self.session() as db:
            self.version(db)
            seed(db); db.commit()
        company, company_headers = self.account('empresa','vieja@example.com')
        job = self.client.post(f'/empresas/{company}/ofertas',headers=company_headers,json={'titulo':'Oferta anterior','descripcion':'Anterior',**DETAILS}).json()
        result = self.client.post('/api/employment/applications',headers=headers,json={'oferta_id':job['id'],'formulario_version':1,'consentimiento':True})
        self.assertEqual(result.status_code,201,result.text)
        with tempfile.TemporaryDirectory() as folder, self.session() as db:
            for uid,key in [(graduate,'e'*32),(company,'c'*32)]:
                db.add(ArchivoPortfolio(id=key,usuario_id=uid,tipo='foto',nombre='Foto.png',mime='image/png',tamano=100,pathname=f'test/{key}.png',verificado=True))
            db.flush()
            db.query(PerfilEmpresa).filter_by(usuario_id=company).one().foto_id='c'*32
            db.query(PerfilEgresado).filter_by(usuario_id=graduate).one().portfolio={'foto_id':'e'*32,'titular':'Conservar','publico':True}
            db.commit()
            before = graduate_snapshot(db)
            backup=Path(folder)/'private-backup.json'
            counts = reset_companies(db,backup)
            db.commit()
            self.assertEqual(counts,{'empresas_eliminadas':11,'ofertas_eliminadas':101,'postulaciones_eliminadas':1,'empresas_creadas':10,'ofertas_creadas':100})
            self.assertEqual(graduate_snapshot(db),before)
            self.assertEqual(db.query(Postulacion).count(),0)
            self.assertEqual(db.query(PerfilEmpresa).count(),10)
            self.assertEqual(db.query(ArchivoPortfolio).count(),1)
            saved=json.loads(backup.read_text(encoding='utf-8'))['tables']
            self.assertEqual(len(saved['usuarios']),11)
            self.assertEqual(len(saved['postulaciones']),1)
            self.assertEqual(saved['archivos_portfolio'][0]['id'],'c'*32)
            self.assertEqual(seed(db),0)
            db.commit()
        self.assertEqual(self.client.get('/auth/me',headers=company_headers).status_code,401)
        self.assertEqual(self.client.get('/auth/me',headers=headers).status_code,200)

    def test_seed_failure_rolls_back_deletes_and_keeps_private_backup(self):
        company,_ = self.account('empresa','anterior@example.com')
        with tempfile.TemporaryDirectory() as folder, self.session() as db:
            self.version(db)
            backup=Path(folder)/'backup.json'
            with patch('scripts.seed_jobs.seed',side_effect=RuntimeError('Simulated insert failure')):
                with self.assertRaises(RuntimeError):
                    reset_companies(db,backup)
            db.rollback()
            self.assertIsNotNone(db.get(Usuario,company))
            self.assertEqual(db.query(PerfilEmpresa).count(),1)
            self.assertTrue(backup.exists())
