from pathlib import Path
import json
import sys
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH

ROOT=Path(__file__).resolve().parent
DATA=json.loads((ROOT/'resultados.json').read_text(encoding='utf-8'))
QA=ROOT/'revision'; QA.mkdir(exist_ok=True)

def setup():
    d=Document(); s=d.sections[0]
    s.page_width=Inches(8.5); s.page_height=Inches(11)
    s.top_margin=s.bottom_margin=Inches(.65)
    s.left_margin=s.right_margin=Inches(.7)
    for name in ['Normal','Title','Subtitle','Heading 1','Heading 2']:
        st=d.styles[name]; st.font.name='Calibri'; st.font.color.rgb=RGBColor(0,0,0)
        pr=st.element.get_or_add_pPr()
        for old in list(pr.findall(qn('w:pBdr'))): pr.remove(old)
        bd=OxmlElement('w:pBdr'); bottom=OxmlElement('w:bottom'); bottom.set(qn('w:val'),'nil'); bd.append(bottom); pr.append(bd)
        rpr=st.element.get_or_add_rPr()
        for fonts in rpr.findall(qn('w:rFonts')):
            for key in ['asciiTheme','hAnsiTheme','eastAsiaTheme','cstheme']:
                fonts.attrib.pop(qn('w:'+key),None)
        lang=OxmlElement('w:lang'); lang.set(qn('w:val'),'es-CL'); rpr.append(lang)
    st=d.styles['Normal']; st.font.size=Pt(11); st.paragraph_format.space_after=Pt(7); st.paragraph_format.line_spacing=1.05
    d.styles['Title'].font.size=Pt(25)
    d.styles['Heading 1'].font.size=Pt(17)
    d.styles['Heading 2'].font.size=Pt(12)
    for name in ['Heading 1','Heading 2']:
        d.styles[name].paragraph_format.space_before=Pt(8)
        d.styles[name].paragraph_format.space_after=Pt(6)
    h=s.header.paragraphs[0]; h.text='BranchIT   |   Evidencia de pruebas funcionales'
    h.runs[0].font.size=Pt(9)
    f=s.footer.paragraphs[0]; f.alignment=WD_ALIGN_PARAGRAPH.RIGHT
    f.add_run('24 de noviembre de 2026   ·   ')
    field=OxmlElement('w:fldSimple'); field.set(qn('w:instr'),'PAGE'); f._p.append(field)
    for r in f.runs: r.font.size=Pt(9)
    d.core_properties.title='Informe de diez casos de prueba de BranchIT'
    d.core_properties.author='Equipo BranchIT'
    return d

def para(d,label,text):
    p=d.add_paragraph(); p.add_run(label+' ').bold=True; p.add_run(text)

def table(d,headers,rows,widths):
    t=d.add_table(rows=1,cols=len(headers)); t.autofit=False
    for i,h in enumerate(headers): t.rows[0].cells[i].text=h
    repeat=OxmlElement('w:tblHeader'); t.rows[0]._tr.get_or_add_trPr().append(repeat)
    for row in rows:
        for c,v in zip(t.add_row().cells,row): c.text=str(v)
    for ri,row in enumerate(t.rows):
        row._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
        for c,w in zip(row.cells,widths):
            c.width=Inches(w); pr=c._tc.get_or_add_tcPr()
            sh=OxmlElement('w:shd'); sh.set(qn('w:fill'),'E8ECF0' if ri==0 else 'FFFFFF'); pr.append(sh)
            borders=OxmlElement('w:tcBorders')
            for edge in ['top','left','bottom','right']:
                e=OxmlElement('w:'+edge)
                for k,v in [('val','single'),('sz','4'),('color','D9D9D9')]: e.set(qn('w:'+k),v)
                borders.append(e)
            pr.append(borders)
            margins=OxmlElement('w:tcMar')
            for edge in ['top','left','bottom','right']:
                e=OxmlElement('w:'+edge); e.set(qn('w:w'),'75'); e.set(qn('w:type'),'dxa'); margins.append(e)
            pr.append(margins)
            for p in c.paragraphs:
                p.paragraph_format.space_after=Pt(2); p.paragraph_format.line_spacing=1.0
                for r in p.runs: r.font.size=Pt(10); r.bold=ri==0
    return t

def selected(r):
    seen=set(); rows=[]
    for c in r['solicitudes']:
        if c['ruta'].startswith('/auth/'): continue
        key=(c['metodo'],c['ruta'],c['http'])
        if key not in seen: rows.append(c); seen.add(key)
    if not rows: rows=r['solicitudes']
    return rows if len(rows)<=7 else rows[:3]+rows[-4:]

def evidence():
    d=setup()
    for i,r in enumerate(DATA['casos']):
        if i: d.add_page_break()
        d.add_paragraph(r['id']+' Resultado de la prueba','Title')
        d.add_heading(r['caso'],1)
        para(d,'Estado',f"{r['resultado']} | {r['segundos']:.3f} s | {len(r['solicitudes'])} solicitudes HTTP")
        para(d,'Ejecución',DATA['fecha'][:19].replace('T',' ')+' hora de Chile')
        para(d,'Procedimiento',r['pasos'])
        para(d,'Comprobaciones aprobadas',r['esperado'])
        d.add_heading('Respuestas reales seleccionadas',2)
        table(d,['Método','Ruta de la API','HTTP'],[(c['metodo'],c['ruta'],c['http']) for c in selected(r)],[.8,5.55,.75])
        d.add_paragraph('')
        para(d,'Entorno',r['simulaciones'])
        para(d,'Origen',r['prueba'])
        d.add_paragraph('Resultado de integración automatizada. Los códigos 4xx esperados demuestran el rechazo correcto. Registro completo en resultados.json y ejecucion.txt. Sin datos ni credenciales de producción.')
    out=QA/'Resultados_para_capturas.docx'; d.save(out); print(out)

def final():
    d=setup()
    d.add_paragraph('Informe de diez casos de prueba de BranchIT','Title')
    d.add_paragraph('Resultados de ejecución y evidencia en imágenes')
    d.add_paragraph('24 de noviembre de 2026')
    d.add_paragraph(f"Los diez casos aprobaron sus verificaciones, con {DATA['solicitudes_totales']} solicitudes HTTP registradas. Se conservaron los cinco casos iniciales y se ejecutaron cinco adicionales. Las imágenes documentan los resultados reales de la ejecución local y se tomaron de las páginas de resultados abiertas en Word.")
    table(d,['Caso','Función evaluada','Estado'],[(r['id'],r['caso'],r['resultado']) for r in DATA['casos']],[.65,5.25,1.2])
    d.add_heading('Alcance de la evidencia',2)
    d.add_paragraph('Las pruebas usan cuentas ficticias y una base temporal aislada. No modifican Neon ni producción. Las capturas muestran resultados automatizados, no recorridos manuales por la interfaz de BranchIT. En CP 10 se simuló Gemini y la fecha; en CP 05 y CP 09 se usan registros de archivos sin subir documentos reales.')
    d.add_paragraph('Los resultados completos se conservan en resultados.json, ejecucion.txt y junit.xml, junto al informe. Los estados 401, 403, 404, 409, 422 y 429 son correctos cuando el caso espera rechazar una operación. No se evaluó carga ni disponibilidad de servicios externos.')
    for r in DATA['casos']:
        d.add_page_break()
        d.add_heading(r['id']+' '+r['caso'],1)
        para(d,'Resultado',f"{r['resultado']} · {r['segundos']:.3f} s · {len(r['solicitudes'])} solicitudes")
        para(d,'Pasos',r['pasos'])
        para(d,'Resultado verificado',r['esperado'])
        image=ROOT/'capturas'/(r['id']+'.png')
        if not image.exists(): raise FileNotFoundError(image)
        picture=d.add_picture(str(image),width=Inches(6.8))
        picture._inline.docPr.set('descr','Captura de Word con el resultado '+r['id']+' '+r['caso'])
        p=d.add_paragraph('Evidencia '+r['id']+' Captura de los resultados mostrados en Word')
        p.runs[0].italic=True; p.runs[0].font.size=Pt(9)
        para(d,'Condiciones',r['simulaciones'])
    out=ROOT/'BranchIT_Informe_10_Casos_Prueba_2026-11-24.docx'; d.save(out); print(out)

if __name__=='__main__':
    final() if '--final' in sys.argv else evidence()
