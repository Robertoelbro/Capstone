from pathlib import Path
p=Path('frontend/src/pages/Apply.jsx');s=p.read_text(encoding='utf-8');s=s.replace('export default function Apply()', 'import { ValidatedForm, PhoneField } from "../Components/FormFields";\nimport AnswerField from "../Components/AnswerField";\nimport JobFacts from "../Components/JobFacts";\n\nexport default function Apply()')
s=s.replace('form.get(`answer_${q.id}`) || ""','q.tipo === "seleccion_multiple" ? form.getAll(`answer_${q.id}`) : form.get(`answer_${q.id}`) || ""')
s=s.replace('Postula a tu próxima oportunidad','Postular').replace('<p>{job.descripcion}</p>','<p>{job.descripcion}</p>\n            <JobFacts job={job} />')
s=s.replace('<form className="tarjeta"','<ValidatedForm className="tarjeta"').replace('</form>','</ValidatedForm>')
a=s.index('              <div className="campo">\n                <label htmlFor="telefono">');b=s.index('              <div className="campo">',a+40)
s=s[:a]+'              <PhoneField label="Teléfono de contacto (opcional)" />\n'+s[b:]
a=s.index('              {job.preguntas.map((q) => (');b=s.index('              <label className="consent">',a)
s=s[:a]+'              {job.preguntas.map((q) => <AnswerField key={q.id} question={q} />)}\n'+s[b:]
p.write_text(s,encoding='utf-8')
p=Path('frontend/src/pages/Applications.jsx');s=p.read_text(encoding='utf-8').replace('item.datos.respuestas[q.id] || "Sin respuesta"','Array.isArray(item.datos.respuestas[q.id]) ? item.datos.respuestas[q.id].join(", ") || "Sin respuesta" : item.datos.respuestas[q.id] || "Sin respuesta"');p.write_text(s,encoding='utf-8')
p=Path('frontend/src/pages/Home.jsx');s=p.read_text(encoding='utf-8');s='import JobFacts from "../Components/JobFacts";\n'+s;s=s.replace('<p>{job.descripcion}</p>','<p>{job.descripcion}</p>\n                  <JobFacts job={job} />');p.write_text(s,encoding='utf-8')
p=Path('frontend/src/pages/PerfilEgresado.jsx');s=p.read_text(encoding='utf-8');s='import { ValidatedForm, SearchField, PhoneField } from "../Components/FormFields";\nimport { careers } from "../data/catalogs";\n'+s
s=s.replace('<form className="portfolio-editor"','<ValidatedForm className="portfolio-editor"').replace('</form>','</ValidatedForm>')
s=s.replace('type={type}','type={type === "number" ? "text" : type}\n          inputMode={type === "number" ? "numeric" : undefined}\n          pattern={type === "number" ? "[0-9]{4}" : undefined}')
a=s.index('                <Field\n                  label="Carrera"');b=s.index('                <Field\n                  label="Año de egreso"',a)
s=s[:a]+'                <SearchField label="Carrera" options={careers} value={form.carrera || ""} onChange={(v) => base("carrera", v)} />\n'+s[b:]
s=s.replace('{field("contacto_telefono", "Teléfono de contacto", "tel", 30)}','<PhoneField label="Teléfono de contacto" value={p.contacto_telefono} onChange={(v) => update("contacto_telefono", v)} />')
import re
s=re.sub(r'\s*<span className="section-number">.*?</span>', '', s, flags=re.S)
s=re.sub(r'\s*<span className="eyebrow">TU ESPACIO, A TU MANERA</span>', '', s)
for old,new in {'Empecemos por ti.':'Perfil','Un minuto para conocerte.':'Video de presentación','Lo que sabes hacer.':'Habilidades','Tus certificaciones.':'Certificaciones','Proyectos con tu sello.':'Proyectos','Contacto y disponibilidad.':'Contacto y disponibilidad','Tu estilo. Tus decisiones.':'Apariencia y privacidad','Tu titular · ¿qué te mueve?':'Titular profesional','Tu historia · formación, intereses y lo que quieres aportar':'Presentación','Qué construiste y qué aprendiste':'Descripción del proyecto','Publicar mi portafolio y sus archivos para compartirlo mediante un enlace':'Publicar portafolio y archivos','Mostrar mi correo en el portafolio público':'Mostrar correo público','Mostrar mi teléfono en el portafolio público':'Mostrar teléfono público','Cambios guardados. Tu portafolio está actualizado.':'Cambios guardados.','Enlace copiado. Ya puedes compartirlo.':'Enlace copiado.'}.items():s=s.replace(old,new)
s=s.replace('              <p>Cuenta qué te apasiona, qué has aprendido y qué buscas.</p>\n','')
a=s.index('              <p>\n                Al despublicar,');b=s.index('              </p>',a)+len('              </p>')
s=s[:a]+'''              <details><summary>Privacidad de los archivos</summary><p>Al despublicar se oculta tu perfil. Los enlaces de archivos ya abiertos pueden durar hasta 5 minutos. Los enlaces externos dependen de la privacidad de su servicio.</p></details>'''+s[b:]
p.write_text(s,encoding='utf-8')
p=Path('frontend/src/pages/PerfilEmpresa.jsx');s=p.read_text(encoding='utf-8');s='import { ValidatedForm } from "../Components/FormFields";\n'+s;s=s.replace('<form ', '<ValidatedForm ').replace('</form>','</ValidatedForm>');s=re.sub(r'\s*<span className="eyebrow">.*?</span>','',s);s=s.replace('        <p className="muted">Cuenta quiénes son y qué quieren construir con nuevos talentos.</p>','');p.write_text(s,encoding='utf-8')
p=Path('frontend/src/Components/FormFields.css');s=p.read_text(encoding='utf-8');s+='\n.auth-layout.auth-layout-compact { display: block; max-width: 700px; margin: 24px auto; min-height: auto; }\n.auth-layout-compact .auth-form-panel { width: 100%; padding: clamp(20px, 5vw, 48px); }\n';p.write_text(s,encoding='utf-8')
