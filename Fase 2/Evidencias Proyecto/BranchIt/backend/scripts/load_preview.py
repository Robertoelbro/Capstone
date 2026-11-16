r"""Bounded read-only HTTP load check for an explicitly isolated PostgreSQL QA API.

Never accepts production aliases or arbitrary URLs. Requires a private manifest,
an origin allowlist and a server-side QA/database attestation before sending JWT.
No login loops, writes, IA, files or billing requests are included.
"""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
from threading import Event, Lock
from time import monotonic, perf_counter
from urllib.parse import urlsplit

import httpx

ROOT = Path(__file__).resolve().parents[1]
PRODUCTION_HOSTS = {'branchit-api.vercel.app', 'branchit-blue.vercel.app'}
QA_ALIAS_HOSTS = {'branchit-qa-api-roberto-el-bro.vercel.app'}


def validate_manifest(data):
    if not isinstance(data, dict):
        raise ValueError('El manifiesto debe ser un objeto JSON.')
    origin = data.get('origin', '')
    if not isinstance(origin, str):
        raise ValueError('Origen inválido.')
    parsed = urlsplit(origin)
    if (parsed.username or parsed.password or parsed.path not in ('', '/') or parsed.query or parsed.fragment
            or not parsed.hostname or parsed.hostname in PRODUCTION_HOSTS):
        raise ValueError('No se permite una URL con credenciales, ruta, parámetros ni alias de producción.')
    local = parsed.hostname in ('localhost', '127.0.0.1')
    if local:
        if parsed.scheme not in ('http', 'https') or data.get('target') != 'local':
            raise ValueError('El destino local debe declararse como local.')
    elif (parsed.scheme != 'https' or data.get('target') != 'preview' or parsed.port not in (None, 443)
          or not re.fullmatch(r'[a-z0-9-]+\.vercel\.app', parsed.hostname)
          or (parsed.hostname not in QA_ALIAS_HOSTS and not re.search(r'-[a-z0-9]{9}-', parsed.hostname))
          or '-git-' in parsed.hostname):
        raise ValueError('Solo se admite localhost o una URL única de preview Vercel incluida en el manifiesto.')
    if data.get('database') != 'postgresql_isolated':
        raise ValueError('La base PostgreSQL aislada debe declararse explícitamente.')
    if not isinstance(data.get('qa_run_id'), str) or not re.fullmatch('[a-f0-9]{32}', data['qa_run_id']):
        raise ValueError('qa_run_id debe ser un UUID hexadecimal de 32 caracteres.')
    for name in ('graduate_id', 'expected_offers'):
        if type(data.get(name)) is not int or not 1 <= data[name] <= 100000:
            raise ValueError(f'{name} debe ser un entero positivo dentro del límite.')
    return origin.rstrip('/')


def validate_response(response, route, manifest):
    if response.status_code != 200:
        return False
    try:
        body = response.json()
    except ValueError:
        return False
    if route == 'session':
        return isinstance(body, dict) and body.get('id') == manifest['graduate_id'] and body.get('tipo') == 'egresado'
    return isinstance(body, list) and len(body) == manifest['expected_offers']


def summarize(rows):
    ordered = sorted(row['ms'] for row in rows)
    percentile = lambda p: round(ordered[math.ceil(len(ordered) * p) - 1], 2) if ordered else None
    return {'requests': len(rows), 'errors': sum(not row['valid'] for row in rows),
            'status_codes': dict(Counter(str(row['status']) for row in rows)),
            'transport_errors': dict(Counter(row.get('error_type', 'HTTPError') for row in rows
                                             if row['status'] == 'transport_error')),
            'p50_ms': percentile(.5), 'p95_ms': percentile(.95)}


def transport_error_type(error):
    """Use fixed labels only: never serialize an exception, request or URL."""
    permitted = (
        (httpx.ReadTimeout, 'ReadTimeout'), (httpx.ConnectTimeout, 'ConnectTimeout'),
        (httpx.PoolTimeout, 'PoolTimeout'), (httpx.WriteTimeout, 'WriteTimeout'),
        (httpx.RemoteProtocolError, 'RemoteProtocolError'),
        (httpx.LocalProtocolError, 'LocalProtocolError'),
        (httpx.ConnectError, 'ConnectError'), (httpx.ReadError, 'ReadError'),
        (httpx.WriteError, 'WriteError'), (httpx.CloseError, 'CloseError'),
        (httpx.ProxyError, 'ProxyError'), (httpx.UnsupportedProtocol, 'UnsupportedProtocol'),
        (httpx.DecodingError, 'DecodingError'),
    )
    return next((label for kind, label in permitted if isinstance(error, kind)), 'HTTPError')


def run(manifest, token, requests=100, concurrencies=(1, 5), timeout=5, max_rps=10, transport=None, bypass=''):
    origin = validate_manifest(manifest)
    if not token or '\n' in token or '\r' in token:
        raise ValueError('Falta QA_GRADUATE_TOKEN válido; no se imprime ni se guarda.')
    if (type(requests) is not int or not 10 <= requests <= 300 or not concurrencies or
            any(type(n) is not int or not 1 <= n <= 10 for n in concurrencies) or
            not 1 <= timeout <= 10 or not 1 <= max_rps <= 10):
        raise ValueError('Límites: 10–300 solicitudes, 1–10 workers, timeout 1–10 s y hasta 10 solicitudes/s.')
    if len(concurrencies) > 3:
        raise ValueError('Máximo tres escenarios por ejecución.')
    shared_headers = {'x-vercel-protection-bypass': bypass} if bypass else {}
    auth_headers = {'Authorization': 'Bearer ' + token}
    targets = [('jobs', '/api/employment/jobs', {}), ('session', '/auth/me', auth_headers),
               ('recommendations', f"/egresados/{manifest['graduate_id']}/recomendaciones", auth_headers)]

    def client():
        return httpx.Client(base_url=origin, headers=shared_headers, timeout=timeout, follow_redirects=False,
                            trust_env=False, transport=transport)

    # No graduate JWT is sent until the server attests its real isolated QA database.
    with client() as check:
        health = check.get('/health/ready')
        if health.status_code != 200 or health.headers.get('X-BranchIT-QA-Run') != manifest['qa_run_id']:
            raise ValueError('Destino no acreditado como QA PostgreSQL aislado; no se enviaron credenciales de egresado.')
        for route, path, headers in targets:
            if not validate_response(check.get(path, headers=headers), route, manifest):
                raise ValueError('Falló la verificación previa de fixtures; no se inicia carga.')

    scenarios = []
    for concurrency in concurrencies:
        stop, lock = Event(), Lock()
        next_send = monotonic()
        started = perf_counter()

        def worker(worker_id):
            nonlocal next_send
            rows = []
            with client() as connection:
                for index in range(worker_id, requests, concurrency):
                    if stop.is_set() or perf_counter() - started >= 60:
                        stop.set()
                        break
                    # Global pacing, not a per-worker rate that grows with concurrency.
                    with lock:
                        now = monotonic()
                        slot = max(now, next_send)
                        next_send = slot + 1 / max_rps
                    if stop.wait(max(0, slot - monotonic())):
                        break
                    route, path, headers = targets[index % len(targets)]
                    begin = perf_counter()
                    error_type = None
                    try:
                        response = connection.get(path, headers=headers)
                        valid, status = validate_response(response, route, manifest), response.status_code
                    except httpx.HTTPError as error:
                        valid, status = False, 'transport_error'
                        error_type = transport_error_type(error)
                    rows.append({'route': route, 'status': status, 'valid': valid,
                                 'error_type': error_type, 'ms': (perf_counter() - begin) * 1000})
                    if not valid:
                        stop.set()  # No retry or sustained pressure after the first error.
                        break
            return rows

        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            batches = list(executor.map(worker, range(concurrency)))
        rows = [row for batch in batches for row in batch]
        elapsed = perf_counter() - started
        result = dict(summarize(rows), concurrency=concurrency, requested=requests,
                      elapsed_seconds=round(elapsed, 3), requests_per_second=round(len(rows) / elapsed, 2),
                      completed=len(rows) == requests and all(row['valid'] for row in rows))
        result['routes'] = {route: summarize([row for row in rows if row['route'] == route]) for route, _, _ in targets}
        scenarios.append(result)
        if not result['completed']:
            break
    return {'timestamp_utc': datetime.now(timezone.utc).isoformat(), 'kind': 'isolated_postgresql_http_smoke',
            'target': manifest['target'], 'origin_sha256': hashlib.sha256(origin.encode()).hexdigest(),
            'dataset_offers': manifest['expected_offers'], 'max_rps': max_rps, 'timeout_seconds': timeout,
            'guard': 'Exact allowlist origin and server QA header checked before sending graduate JWT.',
            'scope': 'Read-only jobs/session/recommendations; no Gemini, Blob, billing or production.',
            'scenarios': scenarios}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--requests', type=int, default=100)
    parser.add_argument('--concurrency', type=int, nargs='+', default=[1, 5])
    parser.add_argument('--timeout', type=float, default=5)
    parser.add_argument('--max-rps', type=float, default=10)
    parser.add_argument('--output', type=Path, default=ROOT.parent / '.vercel' / 'qa-preview-load.json')
    args = parser.parse_args()
    try:
        manifest = json.loads(args.manifest.read_text(encoding='utf8'))
        report = run(manifest, os.getenv('QA_GRADUATE_TOKEN', ''), args.requests, args.concurrency,
                     args.timeout, args.max_rps, bypass=os.getenv('QA_VERCEL_BYPASS', ''))
    except (ValueError, OSError, httpx.HTTPError):
        print('Carga cancelada: revisa allowlist, aislamiento, marcador QA, fixtures y credenciales privadas. No se vuelcan valores.')
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    for scenario in report['scenarios']:
        print(f"workers={scenario['concurrency']} completed={scenario['completed']} "
              f"requests={scenario['requests']} errors={scenario['errors']} p95={scenario['p95_ms']}ms")
    print('Informe sin tokens ni URL privada:', args.output)
    return 0 if all(row['completed'] for row in report['scenarios']) else 1


if __name__ == '__main__':
    raise SystemExit(main())
