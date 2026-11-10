from pathlib import Path
import re
p=Path('frontend/src/pages/Home.jsx');s=p.read_text(encoding='utf-8')
s=s.replace('  FiBriefcase,\n','')
a=s.index('          <div className="hero-copy">');b=s.index('            <div className="hero-links">',a)
s=s[:a]+'''          <div className="hero-copy">
            <h1>Empleo para recién egresados</h1>
'''+s[b:]
a=s.index('          <div className="hero-art"');b=s.index('        </section>',a);s=s[:a]+s[b:]
a=s.index('          <section className="contenedor benefits">');b=s.index('          <section className="contenedor company-cta">',a);s=s[:a]+s[b:]
a=s.index('              <h2>\n                El próximo gran talento');b=s.index('            </div>',a);s=s[:a]+'              <h2>Publica ofertas de empleo</h2>\n'+s[b:]
s=re.sub(r'\s*<span className="eyebrow">.*?</span>','',s,flags=re.S)
s=s.replace('Oportunidades para comenzar','Ofertas de empleo')
p.write_text(s,encoding='utf-8')
p=Path('frontend/src/pages/GraduateHub.jsx');s=p.read_text(encoding='utf-8')
s=re.sub(r'\s*<span className="(?:eyebrow|section-number)">.*?</span>','',s,flags=re.S)
s=s.replace('          <p>Tu próximo paso puede empezar por aquí.</p>','')
s=s.replace('Lo que estás construyendo.','Mis proyectos').replace('Un comienzo a tu medida.','Ofertas de empleo').replace('Semillas que ya plantaste.','Mis postulaciones').replace('Explorar mi siguiente paso','Ver ofertas')
s=re.sub(r'<h2>\s*Oportunidades con.*?</h2>','<h2>Ofertas afines a mi carrera</h2>',s,flags=re.S)
s=re.sub(r'<h2>\s*Un paso pequeño\..*?</h2>','<h2>Completar perfil</h2>',s,flags=re.S)
s=re.sub(r'\s*<div className="hub-note">.*?</div>','',s,flags=re.S)
s=s.replace('Tu primera postulación aparecerá aquí. Las oportunidades te\n                esperan.','Aún no has postulado.')
p.write_text(s,encoding='utf-8')
p=Path('frontend/src/Components/PortfolioView.jsx');s=p.read_text(encoding='utf-8')
s=re.sub(r'\s*<span className="(?:eyebrow|section-number|handwritten)">.*?</span>','',s,flags=re.S)
s=re.sub(r'\s*<div className="cover-note">.*?</div>','',s,flags=re.S)
s=s.replace('"Una historia por construir"','""').replace('"Este espacio espera tu historia: qué te mueve, qué aprendiste y qué te gustaría construir."','"Sin presentación."')
s=re.sub(r'<h2>\s*Mucho más que.*?</h2>','<h2>Sobre mí</h2>',s,flags=re.S)
s=re.sub(r'<h2>\s*Ideas que echan.*?</h2>','<h2>Proyectos</h2>',s,flags=re.S)
s=s.replace('Mi caja de herramientas','Habilidades').replace('<h3>Cada paso deja una rama.</h3>','<h3>Desarrollo profesional</h3>').replace('            <p>Formación, proyectos y aprendizajes que cuentan quién soy.</p>','')
p.write_text(s,encoding='utf-8')
p=Path('frontend/src/Components/Footer/Footer.jsx');s=p.read_text(encoding='utf-8').replace('          <p>El primer paso hacia todo lo que puedes ser.</p>','').replace('        <span>Hecho para quienes están comenzando.</span>','');p.write_text(s,encoding='utf-8')
p=Path('frontend/src/Components/FormFields.css');s=p.read_text(encoding='utf-8').replace('align-items: end','align-items: flex-end');s+='\n.hero.contenedor { grid-template-columns: 1fr; min-height: auto; padding-top: 36px; padding-bottom: 36px; }\n';p.write_text(s,encoding='utf-8')
