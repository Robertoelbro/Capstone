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
        from app.database import engine, SessionLocal
        from scripts.seed_jobs import seed
        from app.models import PerfilEgresado
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
        with SessionLocal() as db:
            seed(db)
            profile=db.query(PerfilEgresado).first()
            profile.apellido='Rojas · Demo'
            profile.presentacion='Me gusta convertir problemas cotidianos en herramientas que hagan la vida más simple.\n\nEstudié Ingeniería en Informática y descubrí que lo que más disfruto es construir en equipo: escuchar una idea, darle forma y verla funcionar. Hoy busco mi primera oportunidad para seguir aprendiendo.'
            profile.portfolio={'titular':'Desarrollo web con curiosidad y propósito.','ubicacion':'Santiago, Chile',
                'disponibilidad':'Inmediata','publico':True,'tema':'bosque',
                'habilidades':[{'nombre':'Python','nivel':'Avanzado'},{'nombre':'React','nivel':'Intermedio'},{'nombre':'SQL','nivel':'Intermedio'},{'nombre':'Git','nivel':'Intermedio'}],
                'proyectos':[{'titulo':'Huerto en casa','descripcion':'Un registro para cuidar plantas, organizar riegos y aprender sobre el cultivo urbano. Proyecto académico de desarrollo web.','tipo':'Académico','tecnologias':['React','Python','PostgreSQL'],'github_url':'https://github.com','proyecto_url':'','video_url':''},
                            {'titulo':'Tiempo compartido','descripcion':'Una idea personal para conectar a vecinos que quieren intercambiar conocimientos. Aprendí a investigar y diseñar una experiencia accesible.','tipo':'Personal','tecnologias':['Figma','JavaScript'],'github_url':'','proyecto_url':'','video_url':''}],
                'certificaciones':[{'nombre':'Fundamentos de desarrollo web · Demo','entidad':'Aprendizaje continuo','url':'https://developer.mozilla.org/es/'}]}
            db.commit()
        print('QA temporal en http://127.0.0.1:8001. Cuentas y datos ficticios; no se usa PostgreSQL.')
        try:
            uvicorn.run(app, host='127.0.0.1', port=8001)
        finally:
            engine.dispose()


if __name__ == '__main__':
    main()
