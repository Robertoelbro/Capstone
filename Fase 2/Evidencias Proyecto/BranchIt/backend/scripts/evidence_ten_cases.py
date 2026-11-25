"""Ten isolated API cases, with sanitized result pages for genuine browser captures."""
import hashlib
import html
import io
import json
import sys
import time
import unittest
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from unittest.mock import patch
import xml.etree.ElementTree as ET

import evidence_five_cases as base
from test_notifications import NotificationTests
from test_offer_forms import OfferForms
from test_ai_daily import DailyAssistantTests

CASES = base.CASES + [
    ('CP-06', 'Notificaciones privadas y contador de lectura', NotificationTests, 'test_events_private_inbox_and_read_state',
     'Postular; consultar bandeja de empresa; intentar marcar desde otra cuenta; leer; cerrar y reabrir convocatoria; marcar todo leído.',
     'Notificación inicial con contador 1; acceso sin sesión 401; lectura ajena 404; lectura propia 204 y contador 0; cierre notificado sin revelar finalista; reapertura agrega una notificación y lectura total deja contador 0.'),
    ('CP-07', 'Campos obligatorios y sueldo de una oferta', OfferForms, 'test_required_details_salary_validation_and_legacy_read',
     'Omitir cada antecedente obligatorio; enviar sueldo cero, negativo, decimal o con puntos; enviar perfiles vacíos; crear oferta válida y consultar sueldo.',
     'Datos faltantes e inválidos rechazados con 422; oferta válida creada con 201 y sueldo 850000 conservado; registros antiguos incompletos pueden cerrarse y requieren completar datos para editarlos.'),
    ('CP-08', 'Respuestas y límites de caracteres al postular', OfferForms, 'test_multiple_choice_and_character_limits_are_validated_and_preserved',
     'Crear preguntas de selección múltiple, texto, párrafo y número; enviar opciones inválidas y textos fuera del límite; enviar respuestas válidas.',
     'Opciones vacías, repetidas o ajenas y números inválidos rechazados con 422; texto de 201 y párrafo de 3001 caracteres rechazados; texto de 200 y párrafo de 3000 aceptados; postulación 201 conserva opciones y tipos.'),
    ('CP-09', 'Límites de video y enlaces del portafolio', base.PortfolioFlows, 'test_file_limits_and_nested_links',
     'Reservar un video de 61 segundos, sin duración, MIME PDF o tamaño excesivo; reservar video válido; probar enlaces inseguros, certificado sin respaldo y correo inválido.',
     'Video inválido y enlaces o datos inseguros rechazados con 422; video de 60 segundos aceptado con 201; solo queda una reserva válida. No se sube un archivo real.'),
    ('CP-10', 'Entrevista diaria y privacidad del historial de IA', DailyAssistantTests, 'test_one_daily_interview_resume_limits_and_next_day',
     'Iniciar entrevista; intentar crear otra el mismo día; intentar acceso desde otra cuenta; continuar hasta seis turnos; probar otro turno y simular el día siguiente.',
     'Inicio 200; segunda entrevista y exceso de turnos 429 sin llamar al proveedor; acceso ajeno 404; reanudación correcta; historial falso ignorado y correo retirado del contexto; conversación cifrada; al día siguiente se permite iniciar otra entrevista.'),
]


def main():
    stamp = datetime.now(ZoneInfo('America/Santiago'))
    folder = base.BACKEND.parent / 'docs' / 'evidencias' / ('diez-casos-' + stamp.strftime('%Y-%m-%d'))
    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'capturas').mkdir(exist_ok=True)
    rows, log = [], io.StringIO()
    original = base.TestClient.request
    for code, title, cls, method, steps, expected in CASES:
        calls = []
        def request(client, verb, url, *args, **kwargs):
            start = time.perf_counter()
            response = original(client, verb, url, *args, **kwargs)
            calls.append({'metodo': verb, 'ruta': str(url), 'http': response.status_code,
                          'ms': round((time.perf_counter()-start)*1000, 2)})
            return response
        start = time.perf_counter()
        with patch.object(base.TestClient, 'request', request):
            result = unittest.TextTestRunner(stream=log, verbosity=2).run(unittest.TestSuite([cls(method)]))
        rows.append({'id':code, 'caso':title, 'prueba':cls.__name__+'.'+method,
                     'pasos':steps, 'esperado':expected, 'resultado':'APROBADO' if result.wasSuccessful() else 'FALLIDO',
                     'segundos':round(time.perf_counter()-start,3), 'solicitudes':calls,
                     'errores':[msg for _,msg in result.failures+result.errors],
                     'simulaciones':'Proveedor Gemini simulado y reloj controlado; no se evalúa la calidad del modelo ni se consume cuota.' if code=='CP-10' else 'Base SQLite aislada y datos ficticios; sin servicios externos.'})
    sources = list((base.BACKEND/'app').rglob('*.py')) + [base.BACKEND/'tests'/name for name in
        ['test_flows.py','test_portfolio.py','test_hiring_release.py','test_notifications.py','test_offer_forms.py','test_ai_daily.py']]
    report = {'fecha':stamp.isoformat(), 'entorno':'API local con base SQLite en memoria y datos ficticios',
              'aprobados':sum(r['resultado']=='APROBADO' for r in rows), 'total':len(rows),
              'casos':rows, 'solicitudes_totales':sum(len(r['solicitudes']) for r in rows),
              'sha256_fuentes':{str(p.relative_to(base.BACKEND)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}}
    (folder/'resultados.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    (folder/'ejecucion.txt').write_text(log.getvalue(),encoding='utf-8')
    suite = ET.Element('testsuite',name='BranchIT diez casos',tests='10',failures=str(10-report['aprobados']))
    for r in rows:
        case=ET.SubElement(suite,'testcase',name=r['id']+' '+r['caso'],time=str(r['segundos']))
        if r['errores']: ET.SubElement(case,'failure').text='\n'.join(r['errores'])
        ET.SubElement(case,'system-out').text=json.dumps(r['solicitudes'],ensure_ascii=False)
    ET.ElementTree(suite).write(folder/'junit.xml',encoding='utf-8',xml_declaration=True)
    esc=html.escape
    for r in rows:
        # Representative requests: one row per distinct method, path and status.
        seen=set(); unique=[]
        for c in r['solicitudes']:
            key=(c['metodo'],c['ruta'],c['http'])
            if key not in seen: unique.append(c); seen.add(key)
        chosen=unique[:3]+unique[-3:] if len(unique)>6 else unique
        trace=''.join(f"<tr><td>{esc(c['metodo'])}</td><td>{esc(c['ruta'])}</td><td>{c['http']}</td></tr>" for c in chosen)
        page=f'''<!doctype html><html lang="es"><meta charset="utf-8"><title>{r['id']} Resultados BranchIT</title>
<style>*{{box-sizing:border-box}}body{{margin:0;background:#f1f3ee;color:#213c30;font:16px/1.4 Arial,sans-serif}}main{{max-width:1120px;margin:20px auto;background:white;padding:25px 32px;border:1px solid #cad4c3;border-radius:14px}}.top{{display:flex;justify-content:space-between;font-size:14px;color:#415547}}h1{{font-size:26px;line-height:1.2;margin:14px 0}}.status{{background:#e4f0db;color:#24471a;padding:8px 12px;font-weight:bold;border-radius:6px;display:inline-block}}p{{margin:12px 0}}table{{border-collapse:collapse;width:100%;font-size:14px}}td,th{{text-align:left;padding:6px 9px;border:1px solid #d9ded4}}th{{background:#edf1e9}}small{{display:block;margin-top:12px;color:#4a5647}}code{{font-size:12px}}</style>
<main><div class="top"><b>BranchIT · Evidencia de prueba de API</b><span>{esc(stamp.strftime('%d-%m-%Y %H:%M'))} · Chile</span></div>
<h1>{r['id']} · {esc(r['caso'])}</h1><div class="status">{r['resultado']} · {r['segundos']} s · {len(r['solicitudes'])} solicitudes</div>
<p><b>Procedimiento:</b> {esc(r['pasos'])}</p><p><b>Resultado verificado por las aserciones:</b> {esc(r['esperado'])}</p>
<table><tr><th>Método</th><th>Respuestas HTTP reales seleccionadas</th><th>HTTP</th></tr>{trace}</table>
<small>{esc(r['simulaciones'])}<br>Captura de resultados automatizados; no corresponde a una prueba manual de la interfaz. Los códigos 4xx esperados verifican el rechazo correcto.<br><code>{esc(r['prueba'])}</code> · Registro completo en resultados.json y ejecucion.txt.</small></main></html>'''
        (folder/(r['id']+'.html')).write_text(page,encoding='utf-8')
    print(log.getvalue())
    print(json.dumps({'carpeta':str(folder),'aprobados':report['aprobados'],'total':10,'solicitudes':report['solicitudes_totales']},ensure_ascii=False))
    return 0 if report['aprobados']==10 else 1

if __name__=='__main__':
    raise SystemExit(main())
