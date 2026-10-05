r"""Opt-in local QA preview. Uses disposable data, never the user's PostgreSQL.

Run from backend: .\.venv\Scripts\python.exe scripts/preview_sprints.py
"""
import os
import secrets
import sys
import tempfile
from pathlib import Path

from cryptography.fernet import Fernet

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    with tempfile.TemporaryDirectory(prefix='branchit-qa-') as directory:
        os.environ['DATABASE_URL'] = 'sqlite:///' + str(Path(directory) / 'preview.db').replace('\\', '/')
        os.environ['SECRET_KEY'] = secrets.token_urlsafe(48)
        os.environ['DATA_ENCRYPTION_KEY'] = Fernet.generate_key().decode()
        os.environ['CORS_ORIGINS'] = 'http://127.0.0.1:5174,http://localhost:5174'
        from alembic import command
        from alembic.config import Config
        config = Config(str(ROOT / 'alembic.ini'))
        command.upgrade(config, 'head')

        from fastapi.testclient import TestClient
        from app.main import app
        from app.database import engine
        import uvicorn

        with TestClient(app) as client:
            company = client.post('/auth/registro/empresa', json={
                'email':'empresa@example.com', 'password':'EmpresaDemo2026!',
                'nombre_empresa':'Horizonte Digital · Demo', 'rubro':'Tecnología'}).json()
            client.post('/auth/registro/egresado', json={
                'email':'egresado@example.com', 'password':'EgresadoDemo2026!',
                'nombre':'Ana', 'apellido':'Demo', 'carrera':'Ingeniería en Informática', 'anio_egreso':2026})
            session = client.post('/auth/login', json={'email':'empresa@example.com','password':'EmpresaDemo2026!'}).json()
            headers = {'Authorization':'Bearer '+session['access_token']}
            client.post(f"/empresas/{company['id']}/ofertas", headers=headers, json={
                'titulo':'Desarrollador/a frontend junior',
                'descripcion':'Oportunidad ficticia para validar el recorrido de BranchIT. Colabora en interfaces web con un equipo que acompaña tus primeros pasos.',
                'requisitos':'Conocimientos de JavaScript y React. Puedes demostrar tu experiencia con proyectos académicos.',
                'ubicacion':'Santiago, Chile', 'modalidad':'hibrido',
                'preguntas':[
                    {'id':'proyecto','etiqueta':'Cuéntanos sobre un proyecto académico','tipo':'parrafo','obligatoria':True},
                    {'id':'disponibilidad','etiqueta':'¿Cuándo podrías comenzar?','tipo':'seleccion','obligatoria':True,'opciones':['De inmediato','En dos semanas','En un mes']}
                ]})
        print('QA temporal en http://127.0.0.1:8001. Cuentas y datos ficticios; no se usa PostgreSQL.')
        try:
            uvicorn.run(app, host='127.0.0.1', port=8001)
        finally:
            engine.dispose()


if __name__ == '__main__':
    main()
