r"""Synthetic local API load smoke; never connects to Neon or a remote service.

Run from backend: .venv\Scripts\python.exe scripts/load_smoke.py
All accounts and offers are disposable. No HTTP port is opened; TestClient
executes the ASGI application in process, so results are NOT Vercel capacity.
"""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import platform
import secrets
import sys
import tempfile
from threading import Barrier
from time import perf_counter
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def summarize(samples):
    durations = sorted(row['ms'] for row in samples)
    percentile = lambda p: round(durations[max(0, math.ceil(len(durations) * p) - 1)], 2)
    return {
        'requests': len(samples),
        'errors': sum(not row['valid'] for row in samples),
        'status_codes': dict(Counter(str(row['status']) for row in samples)),
        'p50_ms': percentile(.50),
        'p95_ms': percentile(.95),
        'max_ms': round(max(durations), 2),
    }


def initialize(directory):
    """Set isolated configuration BEFORE any app import, without reading .env."""
    from cryptography.fernet import Fernet
    os.environ['DATABASE_URL'] = 'sqlite:///' + str(Path(directory) / 'load.db').replace('\\', '/')
    os.environ['SECRET_KEY'] = secrets.token_urlsafe(48)
    os.environ['DATA_ENCRYPTION_KEY'] = Fernet.generate_key().decode()
    os.environ['GEMINI_API_KEY'] = ''
    os.environ['MEDIA_SERVICE_SECRET'] = ''
    # dotenv is patched because the application normally loads backend/.env.
    with patch('dotenv.load_dotenv', return_value=False):
        from fastapi.testclient import TestClient
        from app.main import app
        from app.database import Base, engine, SessionLocal, get_db
        from app import models
        from app.security import create_token, hash_password

    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        password_hash = hash_password(secrets.token_urlsafe(24))
        company = models.Usuario(email='load-company@example.com', tipo=models.TipoUsuario.empresa,
                                 password_hash=password_hash)
        graduate = models.Usuario(email='load-graduate@example.com', tipo=models.TipoUsuario.egresado,
                                  password_hash=password_hash)
        db.add_all([company, graduate])
        db.flush()
        employer = models.PerfilEmpresa(usuario_id=company.id, nombre_empresa='Empresa ficticia de carga')
        db.add(employer)
        db.add(models.PerfilEgresado(usuario_id=graduate.id, nombre='Usuario', apellido='Ficticio',
                                    carrera='Ingeniería en Informática', portfolio={
                                        'habilidades': [{'nombre': 'Python', 'nivel': 'Intermedio'}],
                                        'proyectos': [], 'publico': False}))
        db.flush()
        db.add_all([models.OfertaEmpleo(
            empresa_id=employer.id, titulo=f'Desarrollo Python junior {index + 1}',
            descripcion='Oferta ficticia para una prueba local reproducible.',
            requisitos='Python y SQL', funciones='Construir y mantener aplicaciones Django.',
            perfiles_deseados=['Ingeniería en Informática'], sueldo=850000,
            condiciones_laborales='Datos ficticios. Jornada de prueba.', adaptada_discapacidad=True,
            categoria='Tecnología', modalidad='remoto') for index in range(100)])
        db.commit()
        user_id = graduate.id
        token = create_token(user_id, graduate.token_version)

    def local_database():
        with SessionLocal() as db:
            yield db
    app.dependency_overrides[get_db] = local_database
    targets = [
        ('public_jobs', '/api/employment/jobs', False),
        ('private_session', '/auth/me', True),
        ('recommendations', f'/egresados/{user_id}/recomendaciones', True),
    ]

    def request(client, index):
        name, url, private = targets[index % len(targets)]
        started = perf_counter()
        try:
            response = client.get(url, headers={'Authorization': 'Bearer ' + token} if private else {})
            body = response.json()
            valid = response.status_code == 200 and (
                (isinstance(body, dict) and body.get('id') == user_id) if name == 'private_session'
                else isinstance(body, list) and len(body) == 100)
            status = response.status_code
        except Exception as exc:
            valid, status = False, type(exc).__name__
        return {'route': name, 'ms': (perf_counter() - started) * 1000, 'status': status, 'valid': valid}

    def scenario(concurrency, total):
        # Warm up each route, outside the measured interval.
        with TestClient(app) as client:
            warmup = [request(client, index) for index in range(len(targets))]
        if any(not row['valid'] for row in warmup):
            raise RuntimeError(f'Falló la validación inicial de las rutas; no se publican métricas de un flujo roto: {warmup}')
        barrier = Barrier(concurrency)

        def worker(worker_id):
            with TestClient(app) as client:
                barrier.wait(timeout=30)
                return [request(client, index) for index in range(worker_id, total, concurrency)]

        started = perf_counter()
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            batches = list(executor.map(worker, range(concurrency)))
        elapsed = perf_counter() - started
        samples = [row for batch in batches for row in batch]
        result = dict(summarize(samples), concurrency=concurrency, elapsed_seconds=round(elapsed, 3),
                      requests_per_second=round(total / elapsed, 2))
        result['routes'] = {name: summarize([row for row in samples if row['route'] == name])
                            for name, _, _ in targets}
        return result

    return scenario, lambda: (app.dependency_overrides.clear(), engine.dispose())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--requests', type=int, default=100, help='Solicitudes por escenario (mínimo 30).')
    parser.add_argument('--concurrency', type=int, nargs='+', default=[1, 10])
    parser.add_argument('--output', type=Path, default=ROOT.parent / '.vercel' / 'sprint10-load-smoke.json')
    args = parser.parse_args()
    if not 30 <= args.requests <= 5000 or any(not 1 <= n <= min(50, args.requests) for n in args.concurrency):
        parser.error('Usa entre 30 y 5000 solicitudes y entre 1 y 50 workers, sin superar las solicitudes.')
    with tempfile.TemporaryDirectory(prefix='branchit-load-') as directory:
        scenario, cleanup = initialize(directory)
        try:
            results = [scenario(n, args.requests) for n in args.concurrency]
        finally:
            cleanup()
    report = {
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'kind': 'local_synthetic_asgi_smoke',
        'python': platform.python_version(), 'platform': platform.system(),
        'dataset': {'companies': 1, 'graduates': 1, 'offers': 100},
        'percentile_method': 'nearest rank',
        'scope': 'SQLite temporal y ASGI en proceso; sin red, Neon, Blob, Gemini ni credenciales reales.',
        'limits': 'No mide cold starts, red, PostgreSQL, navegador ni capacidad de Vercel. No es una auditoría ni un SLA.',
        'scenarios': results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    for result in results:
        print(f"workers={result['concurrency']} requests={result['requests']} errors={result['errors']} "
              f"p50={result['p50_ms']}ms p95={result['p95_ms']}ms rps={result['requests_per_second']}")
    print('Informe sin credenciales:', args.output)
    return 1 if any(item['errors'] for item in results) else 0


if __name__ == '__main__':
    raise SystemExit(main())
