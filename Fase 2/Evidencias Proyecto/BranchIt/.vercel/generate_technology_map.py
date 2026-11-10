from pathlib import Path
import html, math
from PIL import Image, ImageDraw, ImageFont
ROOT=Path.cwd();OUT=ROOT/'docs/mapa-tecnologico';OUT.mkdir(parents=True,exist_ok=True)
W,H=2200,1720
image=Image.new('RGB',(W,H),'#f6f7f2');draw=ImageDraw.Draw(image)
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><title>Mapa tecnológico de BranchIT</title><desc>BranchIT al centro, conectado con diez áreas: frontend, backend, datos, seguridad, despliegue, inteligencia artificial, archivos, pruebas, control de versiones y herramientas.</desc><rect width="100%" height="100%" fill="#f6f7f2"/>']
def font(size,bold=False):return ImageFont.truetype('C:/Windows/Fonts/'+('segoeuib.ttf' if bold else 'segoeui.ttf'),size)
def text(x,y,s,size=20,color='#263e30',bold=False):
 draw.text((x,y),s,font=font(size,bold),fill=color)
 svg.append(f'<text x="{x}" y="{y+size}" fill="{color}" font-family="Segoe UI, Arial, sans-serif" font-size="{size}" font-weight="{700 if bold else 400}">{html.escape(s)}</text>')
def rect(x,y,w,h,fill,stroke=None,r=0):
 draw.rounded_rectangle((x,y,x+w,y+h),radius=r,fill=fill,outline=stroke,width=2)
 svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke or "none"}" stroke-width="2"/>')
def line(points,color='#a2b29c',width=3):
 draw.line(points,fill=color,width=width,joint='curve')
 svg.append('<polyline points="'+' '.join(f'{x},{y}' for x,y in points)+f'" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round"/>')
def circle(x,y,r,color):
 draw.ellipse((x-r,y-r,x+r,y+r),fill=color)
 svg.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}"/>')
text(75,35,'BranchIT',42,bold=True)
text(280,49,'Mapa tecnológico del proyecto',30)
text(75,103,'Tecnologías actuales · Interfaz, servicios y herramientas de desarrollo · 19 de octubre de 2026',20,color='#56664f')
# Lines indicate areas of the same system, not direct browser-to-database access.
connections=[[(900,680),(740,680),(740,430),(330,430),(330,395)],
 [(1100,620),(1100,395)],
 [(1300,680),(1460,680),(1460,430),(1870,430),(1870,395)],
 [(900,735),(570,735)],
 [(900,825),(740,825),(740,970),(570,970)],
 [(1300,735),(1630,735)],
 [(1300,825),(1460,825),(1460,970),(1630,970)],
 [(950,880),(950,1170),(330,1170),(330,1230)],
 [(1100,880),(1100,1230)],
 [(1250,880),(1250,1170),(1870,1170),(1870,1230)]]
for pts in connections:line(pts)

def card(x,y,w,h,title,icon,tint,accent,lines,purpose):
 rect(x+5,y+6,w,h,'#e3e8dc',r=22)
 rect(x,y,w,h,'#fffefb','#cad4c1',r=22)
 rect(x+16,y+16,w-32,57,tint,r=13)
 text(x+32,y+28,title,25,accent,True)
 circle(x+w-55,y+44,20,'#fffefb')
 # All icons are text-based signs, avoiding unlicensed or misleading logos.
 tw=draw.textlength(icon,font=font(17,True));text(x+w-55-tw/2,y+32,icon,17,accent,True)
 for i,s in enumerate(lines):
  text(x+28,y+93+i*31,s,21,'#263e30',i==0)
 text(x+28,y+h-41,purpose,17,'#55654e')

card(90,170,480,225,'Base de datos','DB','#dfebf2','#245b75',
 ['PostgreSQL · Neon','Alembic · Migraciones'], 'Usuarios, ofertas, postulaciones y perfiles.')
card(860,170,480,225,'Seguridad','OK','#f3e5cb','#705025',
 ['JWT · python-jose','bcrypt · Cryptography / Fernet'], 'Sesiones, contraseñas y datos cifrados.')
card(1630,170,480,225,'Despliegue','▲','#e8e2f2','#5c477e',
 ['Vercel','Frontend · API · Funciones de archivos'], 'Publicación y ejecución en la nube.')
card(90,500,480,305,'Frontend','<>','#dfece5','#315d45',
 ['React 18 · JavaScript / JSX','HTML5 · CSS3 · Tailwind CSS','React Router · React Icons','country-flag-icons · PropTypes','libphonenumber-js'], 'Interfaz, navegación y formularios.')
card(90,840,480,275,'Backend / API','PY','#deebf2','#285c74',
 ['Python · FastAPI','Pydantic · SQLAlchemy','psycopg2 · Uvicorn','python-dotenv · tzdata'], 'Reglas de negocio, permisos y acceso a datos.')
card(1630,500,480,275,'Inteligencia artificial','IA','#eee4f3','#68457e',
 ['Google Gemini · API','Presentaciones y entrevistas','Preparación de postulaciones','Orientación sobre certificaciones'], 'El backend envía el contexto a Gemini.')
card(1630,840,480,275,'Archivos y multimedia','UP','#f4e1d4','#885437',
 ['Vercel Blob','file-type · music-metadata','Funciones JavaScript en Vercel'], 'Fotos, videos y certificados.')
card(90,1230,480,270,'Pruebas','OK','#e2ece4','#345e42',
 ['unittest','FastAPI TestClient','SQLite · Base aislada'], 'Pruebas automatizadas sin modificar Neon.')
card(860,1230,480,270,'Control de versiones','git','#f3e0d8','#875039',
 ['Git · GitHub','Branches e historial de cambios','Repositorio compartido del equipo'], 'Colaboración y publicación del código.')
card(1630,1230,480,270,'Herramientas','{}','#e4eaf5','#3d567e',
 ['Node.js · npm · Vite','ESLint · Prettier','PostCSS · Autoprefixer'], 'Dependencias, compilación, estilos y revisión.')
# Central application card inspired by the browser window in the reference.
rect(907,627,400,260,'#dce4d1',r=24);rect(900,620,400,260,'#fffefb','#527434',r=24)
rect(918,638,364,40,'#e4edda',r=10)
for i in range(3):circle(935+i*16,658,4,'#779658')
text(983,693,'BranchIT',42,bold=True)
text(955,757,'Plataforma de empleabilidad',20)
text(977,792,'Egresados ↔ Empresas',20)
text(969,827,'Web · Portafolios · IA',18,'#53634b')
rect(90,1560,2020,111,'#e8edde',r=18)
text(114,1575,'Cómo se conectan',21,bold=True)
text(114,1610,'React → API FastAPI → PostgreSQL / Neon y Gemini. Las funciones de archivos usan Vercel Blob.',21)
text(114,1643,'Las líneas agrupan tecnologías del proyecto; no representan conexiones directas entre cada bloque.',17,'#53634b')
svg.append('</svg>');(OUT/'branchit-mapa-tecnologico.svg').write_text('\n'.join(svg),encoding='utf-8');image.save(OUT/'branchit-mapa-tecnologico.png',optimize=True)
(OUT/'README.md').write_text('''# Mapa tecnológico de BranchIT

Generado el 19 de octubre de 2026 a partir de las dependencias y configuración actuales del proyecto. Inspirado en la referencia visual proporcionada por el usuario, con BranchIT al centro y bloques por área.

Archivos:
- `branchit-mapa-tecnologico.png`: imagen para presentaciones.
- `branchit-mapa-tecnologico.svg`: vector editable y ampliable sin pérdida de calidad.

El mapa muestra herramientas principales y auxiliares usadas directamente, no todas las dependencias transitivas de Python y Node. El código de la interfaz está escrito en JavaScript/JSX. FastAPI es la API principal; las funciones JavaScript de Vercel se ocupan de los archivos. PostgreSQL guarda datos y metadatos en Neon; Vercel Blob guarda los archivos. SQLite se usa en pruebas, no como base de producción. Gemini se consume mediante su API; no se entrena un modelo propio.

WCAG 2.1 es un lineamiento de accesibilidad aplicado a la interfaz, no una biblioteca ni un servicio. Los sitios recomendados para certificarse son recursos externos y no forman parte del stack de ejecución.

Las líneas del mapa indican pertenencia al proyecto, no flujos de red. El flujo principal se muestra en la nota inferior.
''',encoding='utf-8')
print(OUT)
