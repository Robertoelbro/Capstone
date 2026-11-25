"""Build the Word report from observed browser results and genuine app screenshots."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib
import importlib.util
import json
from PIL import Image
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

ROOT=Path(__file__).resolve().parent
DATA=json.loads((ROOT/'resultados_web.json').read_text(encoding='utf-8'))
spec=importlib.util.spec_from_file_location('word_layout',ROOT.parent/'diez-casos-2026-11-24'/'crear_word_diez.py')
layout=importlib.util.module_from_spec(spec); spec.loader.exec_module(layout)
doc=layout.setup()
doc.core_properties.title='Informe de pruebas de BranchIT en la web'
doc.core_properties.subject='Evidencias observadas en la página pública de BranchIT'
doc.add_paragraph('Informe de pruebas de BranchIT en la web','Title')
doc.add_paragraph('Resultados observados y capturas de la aplicación publicada')
doc.add_paragraph('24 de noviembre de 2026 · Horario de Chile')
doc.add_paragraph('Se ejecutaron diez casos mediante los controles visibles de https://branchit-blue.vercel.app en el navegador integrado de ChatGPT. Los diez cumplieron los resultados esperados dentro del alcance público evaluado. Cada caso incluye una captura tomada directamente de BranchIT y una descripción del comportamiento observado.')
layout.table(doc,['Caso','Función evaluada','Resultado'],[(r['id'],r['titulo'],r['estado']) for r in DATA['casos']],[.8,5.0,1.3])
doc.add_heading('Alcance de esta revisión',2)
doc.add_paragraph('Esta versión reemplaza la evidencia anterior basada en resultados de API y capturas de Word. Los casos WEB 01 a WEB 10 corresponden a la interfaz pública realmente recorrida; no se trasladan como aprobados los casos autenticados del informe anterior.')
doc.add_paragraph('No se inició sesión con una cuenta válida, ni se crearon cuentas, ofertas o postulaciones. Contratación, notificaciones, portafolio autenticado e IA quedan fuera de esta ejecución. No se realizaron pagos ni cambios en la configuración de la aplicación. El rechazo de un acceso ficticio inválido y las búsquedas sí se enviaron al sistema publicado.')
doc.add_paragraph('Las capturas conservan el tamaño del navegador durante la sesión. Se omitió cualquier contraseña en texto visible. Los conteos reflejan los datos publicados al momento de probar y pueden cambiar posteriormente.')
evidence={}

def add_image(filename,height=4.55):
    path=ROOT/'capturas'/filename
    with Image.open(path) as im: w,h=im.size
    scale=min(6.8/w,height/h)
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    shape=p.add_run().add_picture(str(path),width=Inches(w*scale),height=Inches(h*scale))
    shape._inline.docPr.set('descr','Captura original de BranchIT '+filename)
    evidence[filename]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'ancho':w,'alto':h}

for r in DATA['casos']:
    doc.add_page_break()
    doc.add_heading(r['id']+' '+r['titulo'],1)
    layout.para(doc,'Resultado',r['estado'])
    t=datetime.fromisoformat(r['fecha'].replace('Z','+00:00')).astimezone(ZoneInfo('America/Santiago'))
    layout.para(doc,'Fecha y hora',t.strftime('%d-%m-%Y %H:%M:%S')+' · Chile')
    layout.para(doc,'Página',r['url'])
    layout.para(doc,'Pasos ejecutados',r['pasos'])
    layout.para(doc,'Resultado esperado',r['esperado'])
    layout.para(doc,'Resultado observado',r['observado'])
    add_image(r['captura'])
    p=doc.add_paragraph('Evidencia '+r['id']+' Captura directa de la página de BranchIT')
    p.runs[0].italic=True; p.runs[0].font.size=Pt(9)
    if r.get('captura_adicional'):
        doc.add_page_break()
        doc.add_heading(r['id']+' Evidencia adicional de los formatos',1)
        doc.add_paragraph('Después de seleccionar Construcción de edificios con el teclado, el formulario muestra el RUT 12.345.678-5 y el teléfono 1234 5678 con bandera de Chile y prefijo +569. Son valores de ejemplo introducidos para comprobar el formato; no se envió el registro.')
        add_image(r['captura_adicional'],6.1)
        p=doc.add_paragraph('Captura directa de BranchIT después de seleccionar el giro comercial')
        p.runs[0].italic=True; p.runs[0].font.size=Pt(9)

out=ROOT/'BranchIT_Informe_Pruebas_Web_2026-11-24.docx'
doc.save(out)
(ROOT/'huellas_capturas.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf-8')
print(out)
print('Casos:',len(DATA['casos']),'Capturas:',len(evidence))
