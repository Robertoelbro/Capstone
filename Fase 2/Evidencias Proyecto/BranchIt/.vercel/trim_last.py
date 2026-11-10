from pathlib import Path
import re
p=Path('frontend/src/Components/PortfolioView.jsx');s=p.read_text(encoding='utf-8');s=re.sub(r'<h2>\s*Pequeños logros\..*?</h2>','<h2>Certificaciones</h2>',s,flags=re.S);s=re.sub(r'<h2>\s*El próximo capítulo.*?</h2>','<h2>Contacto</h2>',s,flags=re.S);s=s.replace('        <small>Un portafolio hecho en BranchIt</small>','');p.write_text(s,encoding='utf-8')
p=Path('frontend/src/pages/GraduateHub.jsx');s=p.read_text(encoding='utf-8');s=re.sub(r'<strong>\s*Tu próximo proyecto.*?</strong>','<strong>Añadir proyecto</strong>',s,flags=re.S);s=re.sub(r'<small>\s*Añade una demo,.*?</small>','',s,flags=re.S);p.write_text(s,encoding='utf-8')
