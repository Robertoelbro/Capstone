"""Execute five real API integration cases and export sanitized, reproducible evidence."""
import hashlib
import html
import io
import json
import os
from pathlib import Path
import sys
import time
import unittest
from datetime import datetime
from zoneinfo import ZoneInfo
from unittest.mock import patch
import xml.etree.ElementTree as ET

BACKEND = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(BACKEND / 'tests'), str(BACKEND)]
# Set before importing the application: never load the production database.
os.environ['DATABASE_URL'] = 'sqlite://'
os.environ['SECRET_KEY'] = 'isolated-test-key-never-use-in-production-12345'
os.environ['DATA_ENCRYPTION_KEY'] = 'YWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWE='

from fastapi.testclient import TestClient
from test_flows import AccountFlows
from test_portfolio import PortfolioFlows
from test_hiring_release import HiringReleaseTests

CASES = [
    ('CP-01', 'Registro e inicio de sesión del egresado', AccountFlows, 'test_registration_login_profile_and_delete',
     'Registrar e iniciar sesión; consultar y editar perfil; eliminar cuenta.',
     'Registro 201, login 200, contraseña distinta del texto original, edición 200, eliminación 204 y sesión posterior 401.'),
    ('CP-02', 'Correo duplicado y credenciales incorrectas', AccountFlows, 'test_duplicate_and_invalid_credentials',
     'Repetir un correo con mayúsculas; intentar ingresar con contraseña incorrecta y con usuario inexistente.',
     'Correo duplicado 409; ambos intentos inválidos 401 con el mismo mensaje genérico.'),
    ('CP-03', 'Ofertas y permisos por rol y propietario', AccountFlows, 'test_jobs_and_authorization',
     'Crear una oferta como empresa; intentar acceso sin sesión, como egresado y como otra empresa; cerrar y eliminar oferta.',
     'Sin sesión 401, rol incorrecto 403, creación 201; acceso ajeno rechazado; cierre retira la oferta del listado público y eliminación 204.'),
    ('CP-04', 'Publicación voluntaria y privacidad del portafolio', PortfolioFlows, 'test_publication_and_contact_are_opt_in',
     'Consultar perfil privado; publicar; revisar contacto oculto; habilitar correo; despublicar.',
     'Perfil privado 404; publicación 200 sin correo/teléfono; correo visible solo al autorizarlo; despublicación vuelve a 404.'),
    ('CP-05', 'Contratación, bloqueo y reserva del finalista', HiringReleaseTests, 'test_selected_candidate_is_hired_other_candidates_remain_private',
     'Crear oferta y dos postulaciones; seleccionar finalista; intentar nueva postulación; revisar datos visibles del otro candidato y liberar con PDF ficticio.',
     'Cierre 200; contratado bloqueado con 409; otro candidato habilitado sin conocer selección ni fecha; fecha original conservada; liberación antes de un año habilita búsqueda.'),
]


def main():
    stamp = datetime.now(ZoneInfo('America/Santiago'))
    folder = BACKEND.parent / 'docs' / 'evidencias' / ('cinco-casos-' + stamp.strftime('%Y-%m-%d'))
    folder.mkdir(parents=True, exist_ok=True)
    rows, output = [], io.StringIO()
    original = TestClient.request
    for code, title, cls, method, steps, expected in CASES:
        calls = []
        def request(client, verb, url, *args, **kwargs):
            start = time.perf_counter()
            response = original(client, verb, url, *args, **kwargs)
            calls.append({'metodo': verb, 'ruta': str(url), 'http': response.status_code,
                          'ms': round((time.perf_counter() - start) * 1000, 2)})
            return response
        start = time.perf_counter()
        with patch.object(TestClient, 'request', request):
            result = unittest.TextTestRunner(stream=output, verbosity=2).run(unittest.TestSuite([cls(method)]))
        rows.append({'id': code, 'caso': title, 'prueba': cls.__name__ + '.' + method,
                     'pasos': steps, 'esperado': expected, 'resultado': 'APROBADO' if result.wasSuccessful() else 'FALLIDO',
                     'segundos': round(time.perf_counter() - start, 3), 'solicitudes': calls,
                     'errores': [message for _, message in result.failures + result.errors]})
    sources = {str(p.relative_to(BACKEND)): hashlib.sha256(p.read_bytes()).hexdigest()
               for p in sorted((BACKEND / 'app').rglob('*.py'))}
    for name in ['test_flows.py', 'test_portfolio.py', 'test_hiring_release.py']:
        p = BACKEND / 'tests' / name
        sources[str(p.relative_to(BACKEND))] = hashlib.sha256(p.read_bytes()).hexdigest()
    report = {'fecha': stamp.isoformat(), 'entorno': 'API FastAPI local / SQLite en memoria / TestClient',
              'alcance': 'Pruebas automatizadas de integración de API con datos ficticios. No valida interfaz visual, Neon, Vercel ni proveedores externos. El PDF se representa mediante un registro ficticio verificado; no se sube un archivo real.',
              'python': sys.version, 'aprobados': sum(r['resultado'] == 'APROBADO' for r in rows),
              'total': len(rows), 'casos': rows, 'sha256_fuentes': sources}
    (folder / 'resultados.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    (folder / 'ejecucion.txt').write_text(output.getvalue(), encoding='utf-8')
    suite = ET.Element('testsuite', name='BranchIT cinco casos', tests='5', failures=str(5-report['aprobados']))
    for r in rows:
        case = ET.SubElement(suite, 'testcase', name=r['id'] + ' ' + r['caso'], time=str(r['segundos']))
        if r['errores']:
            ET.SubElement(case, 'failure').text = '\n'.join(r['errores'])
        ET.SubElement(case, 'system-out').text = json.dumps(r['solicitudes'], ensure_ascii=False)
    ET.ElementTree(suite).write(folder / 'junit.xml', encoding='utf-8', xml_declaration=True)
    esc = html.escape
    sections = []
    for r in rows:
        trace = ''.join(f"<tr><td>{esc(c['metodo'])}</td><td><code>{esc(c['ruta'])}</code></td><td>{c['http']}</td><td>{c['ms']}</td></tr>" for c in r['solicitudes'])
        error = '<pre>' + esc('\n'.join(r['errores'])) + '</pre>' if r['errores'] else ''
        sections.append(f"<section><h2>{r['id']} · {esc(r['caso'])}</h2><b>{r['resultado']} · {r['segundos']} s</b><p><strong>Pasos:</strong> {esc(r['pasos'])}</p><p><strong>Resultado esperado y verificado por las aserciones:</strong> {esc(r['esperado'])}</p><p>Prueba: <code>{esc(r['prueba'])}</code></p>{error}<details><summary>Ver {len(r['solicitudes'])} respuestas reales de la API</summary><table><tr><th>Método</th><th>Ruta</th><th>HTTP</th><th>ms</th></tr>{trace}</table></details></section>")
    page = f"""<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>BranchIT · Evidencia de cinco casos</title><style>body{{font:16px/1.6 system-ui,sans-serif;max-width:1040px;margin:40px auto;padding:0 20px;background:#f5f6ef;color:#243d30}}h1{{font-size:32px}}section{{background:white;border:1px solid #c9d5bc;border-radius:16px;padding:24px;margin:24px 0}}b{{color:#365a25}}table{{border-collapse:collapse;width:100%;margin-top:18px}}th,td{{text-align:left;padding:8px;border-bottom:1px solid #dde3d6}}code{{overflow-wrap:anywhere}}summary{{cursor:pointer;font-weight:600}}pre{{white-space:pre-wrap}}@media print{{details{{display:block}}section{{break-inside:avoid}}}}</style><h1>BranchIT · Evidencia de pruebas</h1><p>{esc(stamp.isoformat())} · <strong>{report['aprobados']} de 5 casos aprobados</strong></p><p>{esc(report['entorno'])}</p><p>{esc(report['alcance'])}</p>{''.join(sections)}<footer>Respuestas HTTP medidas durante esta ejecución. Se omiten cuerpos, cabeceras y credenciales. Evidencia complementaria: resultados.json, ejecucion.txt y junit.xml. Huellas SHA-256 de las fuentes en resultados.json.</footer></html>"""
    (folder / 'informe.html').write_text(page, encoding='utf-8')
    print(output.getvalue())
    print(json.dumps({'aprobados': report['aprobados'], 'total': 5, 'carpeta': str(folder),
                      'casos': [{k:r[k] for k in ['id', 'resultado', 'segundos']} for r in rows]}, ensure_ascii=False))
    return 0 if report['aprobados'] == 5 else 1


if __name__ == '__main__':
    raise SystemExit(main())
