import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {pathToFileURL} from 'node:url';
import {FileBlob,PresentationFile} from '@oai/artifact-tool';
const ROOT='C:/Users/Roberto/Documents/GitHub/Capstone/Fase 2/Evidencias Proyecto/BranchIt';
const SOURCE='C:/Users/Roberto/Downloads/Presentacion proyecto (1).pptx';
const BUILD=ROOT+'/.vercel/presentation-build';
const SKILL='C:/Users/Roberto/.codex/plugins/cache/openai-primary-runtime/presentations/26.1011.11113/skills/presentations';
const p=await PresentationFile.importPptx(await FileBlob.load(SOURCE));
const assetPaths=[BUILD+'/portfolio-actual.png',ROOT+'/.vercel/cierre-empresa.png',ROOT+'/.vercel/ia-entrevista-diaria.png',BUILD+'/media/image10.png'];
const assets=new Map(await Promise.all(assetPaths.map(async f=>[f,new Uint8Array(await fs.readFile(f))])));
const original=[...p.slides.items];
const records=(await fs.readFile(BUILD+'/original-inspect.ndjson','utf8')).trim().split(/\r?\n/).map(JSON.parse);
const ink='#202729',green='#327251';
function txt(sl,text,x,y,w,h,size=24,color=ink,bold=false){
 const s=sl.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 s.text=[{runs:[{run:text,style:{typeface:'Proxima Nova',fontSize:size+'px',color,bold}}],spaceAfter:0,spaceBefore:0,marginLeft:0,indent:0}];
 s.text.style={fontSize:size,color,bold,verticalAlignment:'top',insets:0,wrap:'word'};return s;
}
function clean(i,title){
 const sl=original[i];for(const e of records[i].elements.filter(e=>e.kind==='textbox'))p.delete(e.id);
 txt(sl,title,32.72,53,894,58,33.6);return sl;
}
function notes(sl,text,i){sl.speakerNotes.text=text+(i===undefined?'':'\n\nReferencia: presentación original, diapositiva '+(i+1)+'.\nTexto original conservado para consulta:\n'+records[i].elements.filter(e=>e.text).map(e=>e.text).join('\n'));}
function imageMove(id,x,y,w,h){const im=p.resolve(id);im.frame={left:x,top:y,width:w,height:h};im.fit='contain';}
function lines(sl,items,x=34,y=135,w=570,step=92){items.forEach(([head,sub],i)=>{txt(sl,head,x,y+i*step,w,33,27,green,true);if(sub)txt(sl,sub,x,y+i*step+38,w,48,22);});}
function newSlide(title){const sl=p.slides.add({layoutId:original[1].layout.id});pic(sl,BUILD+'/media/image10.png',0,0,187.83,46.72,'Duoc UC');txt(sl,title,32.72,53,894,58,33.6);return sl;}
function pic(sl,file,x,y,w,h,alt){return sl.images.add({blob:assets.get(file),contentType:'image/png',alt,fit:'contain',position:{left:x,top:y,width:w,height:h}});}
// Original cover, names and visual identity stay intact.
txt(original[0],'Tu carrera. Tu crecimiento.',33,151,760,42,29,'#FFFFFF');
notes(original[0],'Apertura: BranchIT conecta a recién egresados con empresas mediante evidencia de sus capacidades. Presentamos un MVP funcional y la evolución desde el diseño inicial. Avance de octubre de 2026.',0);
let s=clean(1,'Índice');
lines(s,[['01 · La oportunidad','Problema, evidencia y solución'],['02 · A quién ayudamos','Público objetivo y motivación del equipo'],['03 · Cómo lo construimos','Scrum, sprints, tecnologías y arquitectura'],['04 · Del diseño al producto','Avances, riesgos, negocio y próximos pasos']],34,128,860,87);
notes(s,'Recorrido breve: comenzar con el problema, mostrar la propuesta de valor, explicar el trabajo realizado y terminar con una invitación a probar el producto.',1);
s=clean(2,'Problemática');
txt(s,'Se exige experiencia antes de dar\nla primera oportunidad.',34,123,850,83,34,ink,true);
txt(s,'El CV no siempre muestra lo que un egresado ya sabe construir.',34,217,850,40,24);
notes(s,'La evidencia periodística de la presentación original contextualiza las dificultades de inserción laboral. Evitar atribuir a BranchIT cifras de impacto o resultados laborales que aún no han sido medidos. Las imágenes y sus QR se mantienen como antecedentes.',2);
s=clean(3,'Links y evidencia');
txt(s,'Diario USACH',55,129,240,37,24);txt(s,'El Observatodo',332,129,260,37,24);txt(s,'OCEC · UDP',624,129,260,37,24);
txt(s,'Antecedentes del problema · Escanea para revisar las fuentes',34,449,880,36,21,'#616161');
notes(s,'Fuentes y códigos QR de la presentación original. Estos antecedentes describen el problema; no son resultados de una evaluación del producto.',3);
s=clean(4,'Solución propuesta');
lines(s,[['Demostrar talento','Portafolio con proyectos y certificaciones.'],['Conectar con oportunidades','Ofertas y afinidad según el perfil.'],['Llegar mejor preparado','Revisión de presentación y entrevistas con IA.']],34,141,570,112);
imageMove('im/et8bihgb',667,201,230,230);
notes(s,'Valor central: pasar de un CV estático a evidencia visible. El egresado publica voluntariamente un portafolio y controla sus datos de contacto. La afinidad es una regla explicable basada en carrera y habilidades; no es una probabilidad de contratación. Gemini orienta al egresado y no toma decisiones de selección.',4);
s=clean(5,'Público objetivo');
lines(s,[['Egresados','Primer empleo y capacidades por demostrar.'],['Empresas','Talento inicial con evidencia para evaluar.'],['Instituciones · a futuro','Posibles alianzas de formación y empleabilidad.']],34,140,580,111);
imageMove('im/b6hw7i1g',670,236,245,170);
notes(s,'Foco inicial en recién egresados de carreras técnicas y profesionales en Chile y empresas que buscan talento inicial. Las alianzas institucionales son una posibilidad futura, todavía sin validar.',5);
s=clean(6,'Competencias e intereses');
txt(s,'Lo que construimos',34,143,330,38,28,green,true);
txt(s,'Desarrollo web\nBases de datos\nSeguridad y arquitectura\nIntegración de IA',34,199,330,240,25);
txt(s,'Por qué nos importa',610,143,310,38,28,green,true);
txt(s,'También estamos buscando\nnuestra primera oportunidad.\n\nDiseñamos desde un\nproblema que conocemos.',610,201,310,240,25);
imageMove('im/g3e94na9',390,240,184,184);
notes(s,'El proyecto permite aplicar desarrollo de software, modelado de datos, arquitectura, gestión de proyectos e integración de servicios de IA. La motivación del equipo proviene de pertenecer al público objetivo; no sustituye una validación con usuarios externos.',6);
s=clean(7,'Metodología de desarrollo');
txt(s,'Scrum: construir, probar y mejorar.',34,130,870,45,29,green,true);
txt(s,'Roberto Orrego\nDesarrollo · Scrum Master\n\nCristobal Lara\nDesarrollo · Ciberseguridad\n\nMatías Werner\nDesarrollo · Módulo IA',34,203,470,290,23);
imageMove('im/1wv21ora',538,228,385,245);
notes(s,'Roles declarados en la presentación original. Cada sprint entrega avances revisables; los hallazgos de uso y las pruebas orientan la siguiente iteración. La responsabilidad de cada entrega es compartida por el equipo.',7);
s=clean(8,'Sprints · del concepto al MVP');
lines(s,[['1–3 · Base del proyecto','Definición, diseño, cuentas y base de datos.'],['4–6 · Recorrido funcional','Hubs, ofertas, portafolio y postulaciones.'],['7 · Orientación con IA','Gemini, entrevista diaria y preparación por oferta.'],['8–11 · Próximas etapas','Seguimiento, carga, auditoría y entrega final.']],34,125,880,84);
txt(s,'Ya disponible: despliegue en Vercel y datos en Neon.',34,479,880,29,21,green,true);
notes(s,'Se condensan los 11 sprints originales en cuatro etapas. El núcleo funcional y la integración de IA están implementados. Hosting se adelantó respecto del plan original. Seguridad y pruebas son continuas; no declarar concluida una auditoría formal o una prueba de carga. El seguimiento posterior a la contratación y las restricciones por experiencia del sprint 8 requieren revisar alcance y validación. No se entrenó un modelo propio: se integra Gemini mediante instrucciones y contexto. El detalle del plan original queda a continuación.',8);
s=clean(9,'Mapa tecnológico');p.delete('im/2107y583');
const tech=[['Interfaz','React · JavaScript · CSS','Navegación y formularios'],['API','Python · FastAPI · SQLAlchemy','Reglas, permisos y datos'],['Persistencia','PostgreSQL · Neon · Alembic','Datos y migraciones'],['Orientación IA','Google Gemini','Preparación del egresado'],['Archivos','Vercel Blob','Fotos, videos y documentos'],['Entrega y calidad','Vercel · GitHub · unittest','Despliegue y verificación']];
tech.forEach(([a,b,c],i)=>{let x=i%2?500:34,y=132+Math.floor(i/2)*124;txt(s,a,x,y,410,29,22,green,true);txt(s,b,x,y+33,410,35,25,ink,true);txt(s,c,x,y+74,410,29,21,'#616161');});
notes(s,'Mapa actualizado a la implementación: React 18 y Vite para la web; FastAPI con Python, Pydantic y SQLAlchemy para la API; PostgreSQL en Neon y Alembic para versionar el esquema. Vercel aloja web, API y funciones de archivos. Vercel Blob conserva archivos, Gemini brinda orientación y GitHub mantiene el código. Se reemplaza el mapa anterior que mencionaba MySQL y Express. No se presenta JMeter como una prueba ya ejecutada.',9);
const architecture=newSlide('Arquitectura de BranchIT');
function box(label,x,y,w,h){const q=architecture.shapes.add({geometry:'rect',position:{left:x,top:y,width:w,height:h},fill:'#ECF7F0',line:{fill:'#4BA173',width:1.5}});q.text=label;q.text.style={fontSize:21,color:ink,alignment:'center',verticalAlignment:'middle',insets:9};return q;}
const web=box('Web React\nEgresado / empresa',35,227,188,105),api=box('API FastAPI\nPermisos y reglas',337,227,219,105),db=box('Neon · PostgreSQL\nDatos del proyecto',703,133,220,93),ai=box('Google Gemini\nOrientación con IA',703,260,220,93),media=box('Funciones de archivos\nJavaScript',337,391,219,82),blob=box('Vercel Blob\nFotos y documentos',703,391,220,82);
function link(a,b,from='right',to='left'){architecture.shapes.connect(a,b,{kind:'elbow',fromSide:from,toSide:to,line:{fill:'#327251',width:2},tail:{type:'triangle',width:'sm',length:'sm'}});}
link(web,api);link(api,db);link(api,ai);link(web,media,'bottom','left');link(media,blob);
txt(architecture,'HTTPS',244,245,80,30,18,green);txt(architecture,'SQL',640,149,60,26,18,green);txt(architecture,'API',640,275,60,26,18,green);
txt(architecture,'Vercel aloja la web, la API y las funciones de archivos.',35,111,890,33,22);
txt(architecture,'Claves privadas y validación de permisos en los servidores.',35,492,880,28,19,'#616161');
notes(architecture,'Arquitectura simplificada y editable. El navegador consume la API FastAPI mediante HTTPS. La API valida JWT, roles y propiedad de recursos, accede a PostgreSQL a través de SQLAlchemy y solicita orientación a Gemini con una clave privada. Las subidas y descargas se gestionan con funciones JavaScript y Vercel Blob; la autorización también consulta la API. Neon almacena datos; los archivos no se guardan como binarios en las tablas. El diagrama omite conexiones secundarias para facilitar la exposición.');
s=clean(10,'Riesgos y cómo abordarlos');
imageMove('im/qtob6hgr',665,208,255,255);
lines(s,[['Adopción','Validar con egresados y empresas.'],['Costo y cuotas de IA','Una práctica diaria; revisar límites del proveedor.'],['Alcance y capacidad del equipo','Priorizar el MVP y entregas breves.'],['Privacidad y calidad','Permisos, cifrado y pruebas; auditoría pendiente.']],34,133,610,86);
notes(s,'Se conservan los riesgos de diferenciación, costos, equipo pequeño, escasez de empresas y alcance. Las mitigaciones son trabajo continuo, no garantías. Pendientes: piloto con usuarios reales, pruebas de carga y revisión formal de seguridad. Las mejoras de accesibilidad no constituyen certificación WCAG.',10);
s=clean(11,'Modelo de negocio');
txt(s,'Acceso esencial gratuito.',34,137,870,55,36,green,true);
txt(s,'Un futuro plan Premium podría sumar\nherramientas de apoyo a la búsqueda.',34,213,870,83,29);
txt(s,'Hipótesis por validar con egresados y empresas.',34,318,530,80,24,'#616161');
imageMove('im/210725oj',675,324,180,180);
notes(s,'Modelo propuesto, no ingresos actuales. El MVP se desarrolla con servicios gratuitos y sin cobros implementados. El contenido del plan Premium debe validarse antes de definir precios. La idea original de 10 postulaciones automáticas al día no está implementada y no se ofrece como funcionalidad actual. No hay evidencia de disposición a pagar ni de alianzas institucionales vigentes.',11);
s=clean(12,'Mockup de referencia');
imageMove('im/ri983e18',34,153,430,282);imageMove('im/qhg7a9kn',496,153,430,282);
txt(s,'Diseño inicial',34,120,400,30,22,green,true);txt(s,'Portafolio y árbol profesional',496,120,430,30,22,green,true);
txt(s,'Punto de partida visual para la evolución del producto.',34,461,890,34,23);
notes(s,'Se conservan los dos mockups de la presentación original y se corrige la imagen que estaba fuera de la diapositiva. Son referencias de diseño; las siguientes diapositivas muestran capturas del producto desarrollado.',12);
const grad=newSlide('Avances · el egresado muestra su talento');
pic(grad,BUILD+'/portfolio-actual.png',34,139,595,335,'Portafolio profesional de Ana Rojas, datos ficticios de demostración');
lines(grad,[['Portafolio compartible','Proyectos y certificaciones.'],['Perfil con evidencia','Archivos, videos y experiencia.'],['Más control','Publicación y contacto voluntarios.']],657,153,278,101);
txt(grad,'Captura del MVP · Datos ficticios de demostración',34,485,850,26,18,'#616161');
notes(grad,'Recorrido sugerido para la demo: registrar un egresado, completar el portafolio, añadir habilidades y proyectos y publicar voluntariamente el enlace. El perfil incorpora foto, video de presentación de hasta un minuto, certificaciones mediante documentos o enlaces, demos, repositorio, QR, experiencia laboral sin exigencia de título y enlace al título. El contacto es opcional en el portafolio público. La captura corresponde a un entorno local de prueba, no a un usuario real. La afinidad con ofertas usa carrera y habilidades y se muestra discretamente en las diez ofertas más afines.');
const progress=newSlide('Avances · selección y preparación');
pic(progress,ROOT+'/.vercel/cierre-empresa.png',34,151,535,301,'Vista de ofertas creadas de una empresa y cierre de convocatoria en entorno de prueba');
const aiPicture=pic(progress,ROOT+'/.vercel/ia-entrevista-diaria.png',588,151,340,301,'Modo IA: interfaz de práctica diaria en entorno local sin conexión a Gemini');
aiPicture.crop={left:0.48,top:0.03,right:0.03,bottom:0.03};
txt(progress,'Empresas',34,119,515,31,25,green,true);txt(progress,'Modo IA',588,119,330,31,25,green,true);
txt(progress,'Ofertas, candidatos y cierre privado.',34,462,535,37,21);txt(progress,'Preparar una entrevista diaria.',588,462,340,37,21);
txt(progress,'Capturas de prueba · Datos ficticios · IA sin conexión en esta captura',34,501,880,24,17,'#616161');
notes(progress,'Empresas: editar información y foto, crear ofertas con sueldo mensual bruto CLP, funciones, información del cargo, perfiles deseados, condiciones y accesibilidad; agregar preguntas interactivas; revisar antecedentes y portafolio de candidatos. Los postulantes se ordenan por afinidad calculada con reglas; los diez primeros se destacan. Se pueden cerrar convocatorias y guardar la persona seleccionada de forma privada. Los egresados ven el cierre, no la identidad elegida. Las notificaciones reflejan cambios. IA: integración Gemini implementada para revisar presentación, explicar requisitos de una oferta, practicar una entrevista diaria de cinco preguntas y recibir retroalimentación; recomienda sitios oficiales para certificaciones. La captura de IA es de un entorno local sin clave: ilustra la interfaz y no una respuesta real del proveedor. No se entrenó un modelo propio ni se automatiza la contratación. Los 100 empleos y 10 empresas de prueba son datos ficticios, no tracción comercial.');
s=clean(13,'Conclusión');
txt(s,'La primera oportunidad\nempieza con evidencia.',34,140,550,126,39,green,true);
txt(s,'Un MVP para mostrar talento,\nconectar y prepararse mejor.',34,295,520,93,28);
txt(s,'Próximo paso: validar con usuarios reales.',34,414,550,55,23);
imageMove('im/nil4jmxk',641,144,270,275);
txt(s,'branchit-blue.vercel.app',606,447,320,35,23,green,true);
notes(s,'Cierre sugerido: invitar al docente y a posibles usuarios a probar el recorrido de egresado y empresa. El objetivo es facilitar que el talento inicial sea visible; no prometer empleo ni resultados de contratación. Próximos pasos: piloto real, medir facilidad de uso y pertinencia, completar validación de carga y seguridad y ajustar el alcance de las funciones futuras. La URL pública sirve para la demostración; verificar el último despliegue antes de exponer.',13);
const orderInfo=await p.inspect({select:'$.slides[*]',include:['id','index']});
const orderRows=orderInfo.ndjson.trim().split(/\r?\n/).map(JSON.parse);
const canonical=orderRows.map(x=>x.id);
p.slides.reorder([...canonical.slice(0,10),canonical[14],...canonical.slice(10,13),canonical[15],canonical[16],canonical[13]]);
await fs.mkdir(BUILD+'/render',{recursive:true});
await (await PresentationFile.exportPptx(p)).save(BUILD+'/candidate.pptx');
for(let i=0;i<p.slides.items.length;i++){await fs.writeFile(BUILD+'/render/slide-'+String(i+1).padStart(2,'0')+'.png',new Uint8Array(await (await p.slides.items[i].export({format:'png',scale:1})).arrayBuffer()));console.log('render',i+1);}
await fs.writeFile(BUILD+'/final-inspect.ndjson',(await p.inspect({select:'$.slides[*]',include:['id','index','elements.id','elements.text','elements.position']})).ndjson);
console.log('Candidate exported');
