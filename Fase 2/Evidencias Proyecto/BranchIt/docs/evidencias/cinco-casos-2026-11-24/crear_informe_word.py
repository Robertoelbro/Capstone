from pathlib import Path
import json
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT

ROOT = Path(__file__).resolve().parent
data = json.loads((ROOT / 'resultados.json').read_text(encoding='utf-8'))
doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Inches(8.5), Inches(11)
sec.top_margin = sec.bottom_margin = Inches(.7)
sec.left_margin = sec.right_margin = Inches(.75)
for name in ['Normal', 'Title', 'Subtitle', 'Heading 1', 'Heading 2']:
    st = doc.styles[name]
    st.font.name = 'Calibri'
    st.font.color.rgb = RGBColor(0, 0, 0)
normal = doc.styles['Normal']
normal.font.size = Pt(11)
normal.paragraph_format.space_after = Pt(7)
normal.paragraph_format.line_spacing = 1.08
doc.styles['Title'].font.size = Pt(26)
doc.styles['Heading 1'].font.size = Pt(17)
doc.styles['Heading 2'].font.size = Pt(13)
for name in ['Heading 1', 'Heading 2']:
    doc.styles[name].paragraph_format.space_before = Pt(12)
    doc.styles[name].paragraph_format.space_after = Pt(6)
header = sec.header.paragraphs[0]
header.text = 'BranchIT   |   Validación funcional'
header.style = 'Normal'
header.runs[0].font.size = Pt(9)
footer = sec.footer.paragraphs[0]
footer.alignment = WD_ALIGN_PARAGRAPH.RIGHT
footer.add_run('24 de noviembre de 2026   ·   Página ')
fld = OxmlElement('w:fldSimple'); fld.set(qn('w:instr'), 'PAGE'); footer._p.append(fld)
for r in footer.runs: r.font.size = Pt(9)

def p(text, bold_label=None):
    para = doc.add_paragraph()
    if bold_label:
        para.add_run(bold_label + ' ').bold = True
    para.add_run(text)
    return para

def table(headers, rows, widths, size=10):
    t = doc.add_table(rows=1, cols=len(headers))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    for c, text, w in zip(t.rows[0].cells, headers, widths):
        c.text = text; c.width = Inches(w)
        shading = OxmlElement('w:shd'); shading.set(qn('w:fill'), 'E6E9ED'); c._tc.get_or_add_tcPr().append(shading)
        for r in c.paragraphs[0].runs: r.bold = True
    repeat = OxmlElement('w:tblHeader'); t.rows[0]._tr.get_or_add_trPr().append(repeat)
    for values in rows:
        for c, text, w in zip(t.add_row().cells, values, widths):
            c.text = str(text); c.width = Inches(w)
    for row in t.rows:
        props = row._tr.get_or_add_trPr(); props.append(OxmlElement('w:cantSplit'))
        for c in row.cells:
            c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            pr = c._tc.get_or_add_tcPr()
            borders = OxmlElement('w:tcBorders')
            for edge in ['top', 'left', 'bottom', 'right']:
                e = OxmlElement('w:' + edge)
                for k, v in [('val', 'single'), ('sz', '4'), ('color', 'D9D9D9')]: e.set(qn('w:' + k), v)
                borders.append(e)
            pr.append(borders)
            margins = OxmlElement('w:tcMar')
            for edge in ['top', 'left', 'bottom', 'right']:
                e = OxmlElement('w:' + edge); e.set(qn('w:w'), '85'); e.set(qn('w:type'), 'dxa'); margins.append(e)
            pr.append(margins)
            for para in c.paragraphs:
                para.paragraph_format.space_after = Pt(2)
                para.paragraph_format.line_spacing = 1.0
                for run in para.runs: run.font.size = Pt(size)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)
    return t

doc.add_paragraph('Informe de pruebas funcionales de BranchIT', 'Title')
p('Resultados y evidencia de cinco casos de integración de la API', 'Propósito')
p('Ejecución del 24 de noviembre de 2026 a las 20:40, hora de Chile.')
p('Los cinco casos ejecutados aprobaron sus verificaciones. Se registraron 61 solicitudes HTTP sobre la API real con datos ficticios y una base SQLite en memoria. No se modificaron Neon ni los datos de producción.')
doc.add_heading('Resumen de resultados', 1)
table(['Caso', 'Función evaluada', 'Resultado', 'Tiempo'], [(r['id'], r['caso'], r['resultado'], f"{r['segundos']:.3f} s") for r in data['casos']], [.65, 4.0, 1.2, 1.15])
doc.add_heading('Entorno y alcance', 1)
p('Se ejecutaron cinco pruebas existentes del proyecto mediante unittest y FastAPI TestClient. Cada caso creó su propia base de datos en memoria y cerró sus recursos al finalizar. Python utilizado: 3.14.5.')
p('Los casos cubren acceso de egresados y empresas, permisos por propietario, privacidad del portafolio y contratación. Las respuestas de rechazo esperadas forman parte del comportamiento correcto de la aplicación.')
p('Esta validación no acredita la interfaz visual, rendimiento bajo carga, migraciones PostgreSQL ni la disponibilidad de Vercel, Neon, Gemini, Blob o Transbank. El finiquito se representa mediante un registro ficticio verificado; no se subió ni analizó un PDF real.', 'Límites')

short = {
'CP-01': [('POST','/auth/registro/egresado',201),('POST','/auth/login',200),('PUT','/egresados/1',200),('DELETE','/egresados/1',204),('GET','/auth/me',401)],
'CP-02': [('POST','/auth/registro/egresado',409),('POST','/auth/login',401)],
'CP-03': [('POST','/empresas/1/ofertas',401),('POST','/empresas/1/ofertas',403),('POST','/empresas/1/ofertas',201),('GET','/empresas/1/ofertas',403),('DELETE','/empresas/1/ofertas/1',204)],
'CP-04': [('GET','/portfolio/1',404),('PUT','/egresados/1',200),('GET','/portfolio/1',200),('PUT','/portfolio/me',200)],
}

def case(r):
    doc.add_heading(r['id'] + ' ' + r['caso'], 1)
    p(f"{r['resultado']} · {r['segundos']:.3f} segundos · {len(r['solicitudes'])} solicitudes registradas.")
    p(r['pasos'], 'Procedimiento')
    p(r['esperado'], 'Resultado verificado')
    records = []
    if r['id'] in short:
        for method, route, status in short[r['id']]:
            match = next(c for c in r['solicitudes'] if (c['metodo'],c['ruta'],c['http']) == (method, route, status))
            records.append(match)
    else:
        records = [c for c in r['solicitudes'] if '/closure' in c['ruta'] or c['http'] == 409 or '/release' in c['ruta']]
    table(['Método', 'Ruta de la API', 'HTTP'], [(c['metodo'],c['ruta'],c['http']) for c in records], [.85, 5.45, .7], 9)
    p('Prueba automatizada: ' + r['prueba'] + '. Las filas muestran una selección de respuestas reales; el registro completo está en resultados.json.')

for group in [data['casos'][:2], data['casos'][2:4], data['casos'][4:]]:
    doc.add_page_break()
    for r in group: case(r)
    if group[0]['id'] == 'CP-05':
        doc.add_heading('Interpretación del resultado', 2)
        p('La prueba confirmó que seleccionar a un finalista bloquea sus nuevas postulaciones, mientras el otro candidato conserva la posibilidad de postular. También verificó que el historial del otro candidato no revela la selección ni la fecha de contratación y que la fecha inicial no se reemplaza al volver a cerrar la oferta.')
        p('La liberación posterior utilizó una referencia ficticia de finiquito y una duración de empleo inferior a un año. Este resultado valida la regla de negocio de la API, no la autenticidad documental ni la carga física del archivo.')

doc.add_page_break()
doc.add_heading('Evidencia y reproducción', 1)
p('La evidencia se conserva junto a este informe, en docs/evidencias/cinco-casos-2026-11-24 dentro del proyecto.')
table(['Archivo', 'Contenido'], [('resultados.json','Resultados, duración, 61 respuestas HTTP y huellas SHA-256 de las fuentes.'),('ejecucion.txt','Salida original de unittest con los cinco resultados OK.'),('junit.xml','Resultados en formato para herramientas de integración continua.'),('informe.html','Versión navegable con el detalle de las solicitudes.')], [1.55,5.45])
p('Para reproducir la ejecución desde backend, utilizar el entorno del proyecto y ejecutar:')
p(r'.\.venv\Scripts\python.exe scripts/evidence_five_cases.py')
p('El ejecutor omite cuerpos de solicitudes, cabeceras y credenciales. La versión de Starlette emitió una advertencia de deprecación de httpx; esta no produjo fallos en los cinco casos.')
doc.add_heading('Tecnologías utilizadas en el proyecto', 1)
table(['Área', 'Tecnologías'], [
('Interfaz','JavaScript, React 18, HTML, CSS, Tailwind CSS, React Router y React Icons.'),
('Construcción','Vite, npm, PostCSS y Autoprefixer.'),
('API','Python, FastAPI, Pydantic y Uvicorn.'),
('Datos','PostgreSQL en Neon, SQLAlchemy, psycopg2 y Alembic.'),
('Servicios','Vercel, Vercel Blob, Vercel Web Analytics, API Gemini y Webpay Plus en integración.'),
('Seguridad','bcrypt, JWT mediante python-jose y Cryptography/Fernet.'),
('Calidad y versiones','unittest, TestClient, httpx, SQLite, pruebas Node, ESLint, Git y GitHub.')], [1.35,5.65])
p('La lista se verificó en las dependencias y módulos del proyecto. No implica que todos los servicios hayan sido probados en esta ejecución.')
doc.core_properties.title = 'Informe de pruebas funcionales de BranchIT'
doc.core_properties.subject = 'Cinco casos de integración de API ejecutados el 24 de noviembre de 2026'
doc.core_properties.author = 'Equipo BranchIT'
out = ROOT / 'BranchIT_Informe_Pruebas_2026-11-24.docx'
doc.save(out)
print(out)
