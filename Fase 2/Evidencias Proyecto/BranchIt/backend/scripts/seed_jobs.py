"""100 fictitious entry-level jobs. Preview by default; --apply writes atomically.

Run from backend: .venv/Scripts/python scripts/seed_jobs.py [--apply]
Uses DATABASE_URL from environment/.env. Requires alembic upgrade head first.
"""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

CATALOG = {
 'Tecnología': ('Semilla Digital', ['Desarrollador frontend junior','Desarrollador backend junior','Analista de datos junior','QA tester junior','Soporte TI nivel 1','Practicante de ciberseguridad','Desarrollador móvil junior','Analista de sistemas junior','Asistente DevOps','Desarrollador full stack junior'], 'Informática o carrera afín. Fundamentos de programación, bases de datos y trabajo con Git.'),
 'Salud': ('Cuidado Integral', ['Enfermero de atención primaria','Kinesiólogo de rehabilitación','Nutricionista comunitario','Técnico en enfermería','Terapeuta ocupacional','Asistente de laboratorio clínico','Fonoaudiólogo inicial','Asistente de salud dental','Tecnólogo médico inicial','Coordinador de promoción de salud'], 'Formación del área de salud correspondiente al cargo. Registro o habilitación profesional cuando corresponda.'),
 'Administración y finanzas': ('Balance Sur', ['Asistente contable','Analista financiero junior','Asistente administrativo','Analista de remuneraciones junior','Ejecutivo de atención comercial','Asistente de auditoría','Analista de tesorería junior','Asistente de recursos humanos','Analista de control de gestión junior','Asistente de compras'], 'Administración, Contabilidad, Finanzas o carrera afín. Manejo de planillas y organización documental.'),
 'Diseño y comunicación': ('Estudio Brote', ['Diseñador gráfico junior','Diseñador UX/UI junior','Community manager junior','Redactor de contenidos','Asistente de producción audiovisual','Editor de video junior','Diseñador de marca junior','Periodista digital inicial','Ilustrador junior','Asistente de marketing digital'], 'Diseño, Comunicación, Publicidad o carrera afín. Portafolio académico o personal y comunicación escrita.'),
 'Educación': ('Aula Abierta', ['Educador de párvulos','Profesor de matemática inicial','Profesor de lenguaje inicial','Asistente de educación diferencial','Profesor de inglés inicial','Tutor de aprendizaje digital','Profesor de ciencias inicial','Asistente de biblioteca escolar','Coordinador de talleres educativos','Diseñador de material didáctico'], 'Educación o Pedagogía en la especialidad correspondiente. Planificación y acompañamiento del aprendizaje.'),
 'Ingeniería y construcción': ('Raíz Ingeniería', ['Asistente de oficina técnica','Ingeniero civil junior','Dibujante técnico junior','Asistente de arquitectura','Supervisor de obra trainee','Ingeniero eléctrico junior','Ingeniero mecánico junior','Asistente de presupuestos de obra','Modelador BIM junior','Inspector de calidad en construcción'], 'Ingeniería, Arquitectura o Construcción según el cargo. Lectura de planos y herramientas de la especialidad.'),
 'Logística y operaciones': ('Ruta Circular', ['Analista logístico junior','Asistente de comercio exterior','Coordinador de despacho junior','Analista de inventario junior','Planificador de transporte trainee','Asistente de abastecimiento','Analista de operaciones junior','Supervisor de bodega trainee','Asistente de importaciones','Analista de mejora continua junior'], 'Logística, Comercio Exterior o Ingeniería Industrial. Manejo de inventarios y análisis de procesos.'),
 'Turismo y gastronomía': ('Destino Nativo', ['Recepcionista de hotel','Guía de turismo inicial','Asistente de cocina profesional','Asistente de pastelería','Coordinador de eventos junior','Ejecutivo de reservas','Asistente de gestión hotelera','Asistente de turismo sustentable','Encargado de experiencia de visitantes','Asistente de operaciones gastronómicas'], 'Turismo, Hotelería o Gastronomía según el cargo. Atención al cliente y colaboración en equipo.'),
 'Ciencias sociales': ('Comunidad Viva', ['Psicólogo organizacional junior','Trabajador social inicial','Asistente de investigación social','Asistente jurídico','Analista de selección junior','Gestor comunitario junior','Asistente de proyectos sociales','Mediador comunitario inicial','Asistente de estudios cualitativos','Coordinador de voluntariado junior'], 'Psicología, Trabajo Social, Derecho o Ciencias Sociales según el cargo. Ética y comunicación interpersonal.'),
 'Medioambiente y agro': ('Territorio Verde', ['Ingeniero ambiental junior','Asistente de agronomía','Analista de sustentabilidad junior','Técnico forestal inicial','Asistente veterinario profesional','Monitor de educación ambiental','Asistente de laboratorio biológico','Analista de gestión de residuos junior','Asistente de producción agrícola','Inspector ambiental trainee'], 'Formación en ciencias ambientales, agropecuarias o biológicas según el cargo. Interés en sostenibilidad.'),
}

def jobs():
    cities = ['Santiago','Valparaíso','Concepción','Temuco','La Serena','Puerto Montt','Rancagua','Antofagasta','Talca','Valdivia']
    items = []
    for area_index, (area, (company, titles, requirements)) in enumerate(CATALOG.items()):
        for index, title in enumerate(titles):
            remote_area = area in ('Tecnología','Diseño y comunicación','Administración y finanzas')
            mode = ['Remoto','Híbrido','Presencial'][index % 3] if remote_area else 'Presencial'
            items.append({'demo_clave':f'branchit-demo-v1-{area_index:02}-{index:02}',
                'empresa':f'DEMO · {company}', 'categoria':area, 'titulo':title,
                'descripcion':f'OFERTA FICTICIA PARA DEMOSTRACIÓN ACADÉMICA. No es una vacante real.\n\nBuscamos {title.lower()} para integrarse a {company}. Participarás en tareas de {area.lower()}, con acompañamiento de un equipo y espacio para desarrollar tus primeros proyectos. Se valoran los aprendizajes académicos y las iniciativas personales.',
                'requisitos':requirements + ' No se requiere experiencia laboral previa; adjunta proyectos o prácticas relevantes.',
                'ubicacion':cities[index], 'modalidad':mode,
                'preguntas':[{'id':'interes','etiqueta':'¿Qué aprendizaje o proyecto te gustaría aportar?','tipo':'parrafo','obligatoria':True,'opciones':[]}]})
    return items

DEMO_PASSWORD = 'contraseña'

def company_accounts():
    return [{'empresa': f'DEMO · {company}', 'correo': f'seed.branchit.v1.{index}@example.com',
             'contraseña': DEMO_PASSWORD, 'categoria': area, 'publicaciones': 10}
            for index, (area, (company, _, _)) in enumerate(CATALOG.items())]

def seed(db):
    from app.models import Usuario, PerfilEmpresa, OfertaEmpleo, TipoUsuario
    from app.security import hash_password, verify_password
    created = 0
    for index, (area, (company, _, _)) in enumerate(CATALOG.items()):
        email=f'seed.branchit.v1.{index}@example.com'
        user=db.query(Usuario).filter_by(email=email).first()
        if user:
            existing_profile = db.query(PerfilEmpresa).filter_by(usuario_id=user.id).first()
            if (user.tipo != TipoUsuario.empresa or not existing_profile or
                    existing_profile.nombre_empresa != f'DEMO · {company}' or existing_profile.rubro != area or
                    existing_profile.descripcion != 'Empresa ficticia. Datos para demostración académica.'):
                raise RuntimeError('La cuenta reservada para datos demo ya existe con otra configuración. No se modificó.')
            if not verify_password(DEMO_PASSWORD, user.password_hash):
                user.password_hash = hash_password(DEMO_PASSWORD)
                user.token_version += 1
            user.activo = True
        if not user:
            user=Usuario(email=email,password_hash=hash_password(DEMO_PASSWORD),tipo=TipoUsuario.empresa,activo=True)
            db.add(user); db.flush()
            db.add(PerfilEmpresa(usuario_id=user.id,nombre_empresa=f'DEMO · {company}',rubro=area,
                                 descripcion='Empresa ficticia. Datos para demostración académica.'))
            db.flush()
        company_profile=db.query(PerfilEmpresa).filter_by(usuario_id=user.id).one()
        for item in (j for j in jobs() if j['categoria']==area):
            if db.query(OfertaEmpleo.id).filter_by(demo_clave=item['demo_clave']).first(): continue
            db.add(OfertaEmpleo(empresa_id=company_profile.id, **{k:v for k,v in item.items() if k!='empresa'}))
            created += 1
    db.flush()
    return created

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply',action='store_true',help='Crear/habilitar 10 empresas demo con contraseña de testing e insertar 100 ofertas sin duplicar ni modificar ofertas existentes.')
    args=parser.parse_args()
    if not args.apply:
        print(json.dumps(jobs(),ensure_ascii=False,indent=2))
        print('\n100 ofertas · 10 categorías · vista previa, sin escribir en la base.',file=sys.stderr)
    else:
        from app.database import SessionLocal
        with SessionLocal() as db:
            try:
                count=seed(db)
                db.commit()
                print(f'Insertadas: {count}. Ya existentes: {100-count}.')
            except Exception:
                db.rollback()
                raise
