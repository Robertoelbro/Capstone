from pathlib import Path
import json, subprocess, html, math
from PIL import Image, ImageDraw, ImageFont

ROOT = Path.cwd()
OUT = ROOT / 'docs' / 'diagrama'
OUT.mkdir(parents=True, exist_ok=True)
code = r'''
import os,json
os.environ['DATABASE_URL']='sqlite://'
from app.database import Base
from app import models
from sqlalchemy import UniqueConstraint
from sqlalchemy.schema import CreateTable,CreateIndex
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import CreateEnumType
engine=postgresql.dialect()
tables=[]
for t in Base.metadata.sorted_tables:
 single=set()
 for c in t.constraints:
  if isinstance(c,UniqueConstraint) and len(c.columns)==1: single.add(next(iter(c.columns)).name)
 for i in t.indexes:
  if i.unique and len(i.columns)==1 and i.dialect_options['postgresql'].get('where') is None:single.add(next(iter(i.columns)).name)
 tables.append({'name':t.name,'columns':[{'name':c.name,'type':str(c.type.compile(dialect=engine)),'pk':c.primary_key,'fk':[f.target_fullname for f in c.foreign_keys],'uk':c.name in single,'nullable':c.nullable} for c in t.columns]})
sql=[str(CreateEnumType(models.Usuario.__table__.c.tipo.type).compile(dialect=engine))+';']
for t in Base.metadata.sorted_tables:sql.append(str(CreateTable(t).compile(dialect=engine))+';')
for t in Base.metadata.sorted_tables:
 for i in sorted(t.indexes,key=lambda i:i.name):sql.append(str(CreateIndex(i).compile(dialect=engine))+';')
print(json.dumps({'tables':tables,'sql':'\n\n'.join(sql)},ensure_ascii=False))
'''
result=subprocess.check_output([str(ROOT/'backend/.venv/Scripts/python.exe'),'-c',code],cwd=ROOT/'backend',encoding='utf-8',env={**__import__('os').environ,'PYTHONIOENCODING':'utf-8'})
data=json.loads(result);tables={t['name']:t for t in data['tables']}
(OUT/'branchit.schema.json').write_text(json.dumps(data['tables'],ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'branchit.sql').write_text('-- Estructura generada desde modelos; referencia documental, no ejecutar sobre la BD existente.\n'+data['sql']+'\n',encoding='utf-8')
W,H=2300,2250
image=Image.new('RGB',(W,H),'#f6f7f2'); draw=ImageDraw.Draw(image)
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><title>BranchIT — Diagrama físico de base de datos</title><desc>Ocho tablas y diez claves foráneas, generadas desde los modelos SQLAlchemy.</desc><rect width="100%" height="100%" fill="#f6f7f2"/>']
def font(size,bold=False,mono=False):return ImageFont.truetype('C:/Windows/Fonts/'+('consola.ttf' if mono else 'segoeuib.ttf' if bold else 'segoeui.ttf'),size)
def text(x,y,s,size=17,color='#263e30',bold=False,mono=False):
 draw.text((x,y),s,font=font(size,bold,mono),fill=color)
 svg.append(f'<text x="{x}" y="{y+size}" fill="{color}" font-family="{("Consolas, monospace" if mono else "Segoe UI, Arial, sans-serif")}" font-size="{size}" font-weight="{700 if bold else 400}">{html.escape(s)}</text>')
def rect(x,y,w,h,fill,stroke=None,r=0):
 draw.rounded_rectangle((x,y,x+w,y+h),radius=r,fill=fill,outline=stroke,width=2)
 svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke or "none"}" stroke-width="2"/>')
def line(points,color='#738c79',width=3):
 draw.line(points,fill=color,width=width,joint='curve')
 svg.append(f'<polyline points="'+ ' '.join(f'{x},{y}' for x,y in points)+f'" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round"/>')
def arrow(points,label,lx,ly,color='#738c79'):
 line(points,color)
 x,y=points[-1];px,py=points[-2];a=math.atan2(y-py,x-px)
 head=[(x,y),(x-12*math.cos(a-.45),y-12*math.sin(a-.45)),(x-12*math.cos(a+.45),y-12*math.sin(a+.45))]
 draw.polygon(head,fill=color);svg.append('<polygon points="'+' '.join(f'{x:.1f},{y:.1f}' for x,y in head)+f'" fill="{color}"/>')
 text(lx,ly,label,16,color)
text(90,45,'BranchIT',40,bold=True)
text(285,58,'Diagrama físico de base de datos',27)
text(90,106,'Modelos SQLAlchemy · PostgreSQL / Neon · Migraciones hasta 0008 · 19 de octubre de 2026',19,color='#53634b')
text(90,139,'PK: clave primaria   FK: clave foránea   UK: valor único   ?: campo que permite NULL   Flecha: FK → tabla referenciada',17,color='#53634b')
pos={'archivos_portfolio':(90,220),'usuarios':(850,220),'notificaciones':(1630,220),'perfiles_egresado':(90,900),'perfiles_empresa':(850,900),'postulaciones':(90,1530),'ofertas_empleo':(850,1470),'entrevistas_ia':(1630,1530)}
CARD=480
heights={n:66+len(t['columns'])*29 for n,t in tables.items()}
bottom=lambda n:pos[n][1]+heights[n]
arrow([(570,370),(850,370)],'usuario_id',630,342)
arrow([(1630,370),(1330,370)],'usuario_id',1400,342)
arrow([(330,900),(330,790),(740,790),(740,550),(850,550)],'usuario_id · UK',435,762)
arrow([(1090,900),(1090,bottom('usuarios'))],'usuario_id · UK',1115,728)
arrow([(2110,1660),(2220,1660),(2220,550),(1330,550)],'usuario_id',2050,1030)
arrow([(330,1530),(330,bottom('perfiles_egresado'))],'egresado_id',350,1380)
arrow([(1090,1470),(1090,bottom('perfiles_empresa'))],'empresa_id',1115,1340)
arrow([(570,1650),(850,1650)],'oferta_id',645,1622)
arrow([(1630,1650),(1330,1650)],'oferta_id · opcional',1390,1622)
arrow([(1330,1090),(1450,1090),(1450,715),(330,715),(330,bottom('archivos_portfolio'))],'foto_id · opcional',740,686,'#a47751')
colors={'usuarios':('#dce9d1','#b4c7a3'),'perfiles_egresado':('#e3e9f5','#b7c4df'),'perfiles_empresa':('#f6e5d5','#ddc4aa'),'ofertas_empleo':('#dcece5','#adcbbc'),'postulaciones':('#ece3f3','#cbb7d9'),'archivos_portfolio':('#f3ebcb','#d3c48d'),'notificaciones':('#f5dfdf','#d9b8b8'),'entrevistas_ia':('#deebef','#b0c9d2')}
for name,(x,y) in pos.items():
 t=tables[name];fill,border=colors[name];height=heights[name]
 rect(x+4,y+5,CARD,height,'#e6e9df',r=16);rect(x,y,CARD,height,'#fffefb',border,r=16)
 rect(x+2,y+2,CARD-4,48,fill,r=14)
 text(x+18,y+10,name,23,bold=True)
 for i,c in enumerate(t['columns']):
  row=y+57+i*29
  if i%2:rect(x+3,row-2,CARD-6,28,'#f5f6f0')
  text(x+16,row,c['name']+(' ?' if c['nullable'] else ''),16,mono=True)
  text(x+280,row,c['type'].replace('TIMESTAMP WITHOUT TIME ZONE', 'TIMESTAMP'),14,color='#56645a',mono=True)
  tags=' '.join(tag for tag,v in [('PK',c['pk']),('FK',bool(c['fk'])),('UK',c['uk'])] if v)
  text(x+421,row,tags,13,color='#385d28',bold=True)
rect(90,2115,2020,115,'#e8eddf',r=14)
text(110,2125,'Restricciones adicionales',19,bold=True)
text(110,2154,'Postulaciones: UNIQUE(oferta_id, egresado_id) · Una selección por oferta (índice único parcial).',17)
text(110,2179,'Entrevistas IA: UNIQUE(usuario_id, fecha) · Una sesión diaria por cuenta. El historial y los antecedentes se guardan cifrados.',17)
text(110,2203,'Relaciones: usuario 1 → 0..1 perfil; empresa 1 → N ofertas; egresados N ↔ M ofertas mediante postulaciones. TIMESTAMP: sin zona horaria.',17)
svg.append('</svg>')
(OUT/'branchit.svg').write_text('\n'.join(svg),encoding='utf-8');image.save(OUT/'branchit.png',optimize=True)
mermaid=['erDiagram','    usuarios ||--o| perfiles_egresado : tiene','    usuarios ||--o| perfiles_empresa : tiene','    usuarios ||--o{ archivos_portfolio : posee','    usuarios ||--o{ notificaciones : recibe','    usuarios ||--o{ entrevistas_ia : practica','    perfiles_empresa ||--o{ ofertas_empleo : publica','    perfiles_egresado ||--o{ postulaciones : envia','    ofertas_empleo ||--o{ postulaciones : recibe','    ofertas_empleo |o--o{ entrevistas_ia : contextualiza','    archivos_portfolio |o--o{ perfiles_empresa : foto_opcional']
for n,t in tables.items():
 mermaid.append('    '+n+' {')
 for c in t['columns']:
  ty=c['type'].replace(' ','_').replace('(','_').replace(')','')
  tags=','.join(tag for tag,v in [('PK',c['pk']),('FK',bool(c['fk'])),('UK',c['uk'])] if v)
  mermaid.append(f'        {ty} {c["name"]}'+(' '+tags if tags else '')+(' "nullable"' if c['nullable'] else ''))
 mermaid.append('    }')
(OUT/'branchit.mmd').write_text('\n'.join(mermaid)+'\n',encoding='utf-8')
md='''# Diagrama de base de datos de BranchIT

Generado el 19 de octubre de 2026 desde `backend/app/models.py`. Representa las 8 tablas de aplicación y sus 10 claves foráneas, correspondientes al esquema hasta `0008_entrevista_diaria`. No se consultaron registros ni credenciales de Neon. No es una extracción en vivo: refleja los modelos actuales del proyecto.

- `branchit.html`: visor local con zoom.
- `branchit.png`: imagen para presentaciones.
- `branchit.svg`: imagen vectorial ampliable sin pérdida de calidad.
- `branchit.mmd`: fuente editable en Mermaid.
- `branchit.sql`: DDL PostgreSQL de referencia, NO ejecutar sobre una base existente.
- `branchit.schema.json`: inventario de columnas y claves.

Se excluyen `alembic_version` y los esquemas de respaldo. Las flechas del dibujo van desde la tabla que contiene la FK hacia la tabla referenciada.

Los perfiles de egresado y empresa se vinculan mediante `usuario_id` único. El tipo de cuenta y la aplicación determinan qué perfil corresponde a cada usuario. La FK de foto de empresa es opcional; la propiedad del archivo se valida en la API. Borrar una oferta deja nula su referencia en entrevistas IA (`ON DELETE SET NULL`).

Las experiencias laborales, habilidades, proyectos, certificaciones y enlace al título están dentro del JSON `perfiles_egresado.portfolio`, por lo que no aparecen como tablas independientes. Los binarios de fotos, videos y documentos se almacenan en Vercel Blob; `archivos_portfolio` conserva sus metadatos. Las respuestas y antecedentes de la postulación se guardan en `postulaciones.datos_cifrados`, y la conversación de entrevista en `entrevistas_ia.datos_cifrados`.

## Fuente editable

```mermaid
'''+ '\n'.join(mermaid)+'\n```\n'
(OUT/'README.md').write_text(md,encoding='utf-8')
page='''<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>BranchIT · Diagrama de base de datos</title><style>*{box-sizing:border-box}body{margin:0;font:16px system-ui,sans-serif;background:#f6f7f2;color:#263e30}header{padding:16px 24px;border-bottom:1px solid #ccd6c2;background:#fffefb}h1{font-size:24px;margin:0 0 8px}p{margin:5px 0;color:#4d5d50}nav{display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin-top:12px}button,a{padding:9px 14px;border:1px solid #80946e;border-radius:8px;background:#edf2e4;color:#263e30;font:inherit}a{text-decoration:none}button{cursor:pointer}button:focus-visible,a:focus-visible{outline:3px solid #385d28;outline-offset:3px}main{height:calc(100vh - 175px);overflow:auto;padding:16px}#diagram{display:block;max-width:none;background:white}output{min-width:55px}small{font-size:13px}</style><header><h1>BranchIT · Diagrama de base de datos</h1><p>8 tablas · 10 relaciones · Fuente: modelos del proyecto hasta la migración 0008. Sin datos personales.</p><nav aria-label="Controles del diagrama"><button id="less" aria-label="Reducir zoom">−</button><output id="zoom" aria-live="polite"></output><button id="more" aria-label="Aumentar zoom">+</button><button id="fit">Ajustar al ancho</button><a href="branchit.png" download>Descargar PNG</a><a href="branchit.svg" download>Descargar SVG</a><a href="branchit.sql" download>Ver SQL</a></nav></header><main id="viewport" aria-label="Diagrama ampliable" tabindex="0"><img id="diagram" src="branchit.svg" alt="Diagrama de BranchIT con usuarios, perfiles, ofertas, postulaciones, archivos, notificaciones y entrevistas IA"></main><script>let scale=.5;const img=document.getElementById('diagram');function setScale(s){scale=Math.max(.25,Math.min(2,s));img.style.width=(2300*scale)+'px';document.getElementById('zoom').value=Math.round(scale*100)+'%'}document.getElementById('less').onclick=()=>setScale(scale-.1);document.getElementById('more').onclick=()=>setScale(scale+.1);function fit(){setScale((document.getElementById('viewport').clientWidth-32)/2300)}document.getElementById('fit').onclick=fit;fit();</script></html>'''
(OUT/'branchit.html').write_text(page,encoding='utf-8')
assert len(tables)==8
assert sum(len(c['fk']) for t in tables.values() for c in t['columns'])==10
print('Diagrama generado: 8 tablas / 10 relaciones. Archivos en',OUT)

