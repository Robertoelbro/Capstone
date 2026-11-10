from pathlib import Path
import re
p=Path('frontend/src/pages/OfertasEmpresa.jsx');s=p.read_text(encoding='utf-8')
a=s.index('          <div className="campo">\n            <label htmlFor="descripcion">');b=s.index('          <div className="campo">\n            <label htmlFor="requisitos">',a);block=s[a:b];s=s[:a]+s[b:];s=s.replace('          <MoneyField',block+'          <MoneyField')
a=s.index('          <QuestionEditor');b=s.index('          {editandoId &&',a);block=s[a:b];s=s[:a]+s[b:];s=s.replace('\n          {error && (','\n'+block+'\n          {error && (');p.write_text(s,encoding='utf-8')
p=Path('frontend/src/Components/GraduateLayout.jsx');s=p.read_text(encoding='utf-8');s=re.sub(r'\s*<small className="sidebar-note">.*?</small>','',s,flags=re.S);p.write_text(s,encoding='utf-8')
p=Path('frontend/src/portfolio.js');s=p.read_text(encoding='utf-8');
for old,new in {'Tu historia':'Presentación','Tu formación':'Carrera','Una foto tuya':'Foto','Tus habilidades':'Habilidades','Tu primer proyecto':'Proyecto','Preséntate en video':'Video de presentación'}.items():s=s.replace(old,new)
p.write_text(s,encoding='utf-8')
