"""10 demo companies and 100 current-format jobs. Preview by default.

Run from backend: .venv/Scripts/python scripts/seed_jobs.py [--apply]
Reset: --apply --reset-companies --confirm-reset BORRAR_EMPRESAS_Y_POSTULACIONES
Uses DATABASE_URL from environment/.env. Requires alembic upgrade head first.
"""
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

# One canonical graduate profile per title, in the same order as CATALOG.
PROFILES = {
 'Tecnología': ['Ingeniería en Informática','Ingeniería Civil en Informática','Ingeniería en Informática','Ingeniería en Informática','Técnico en Informática','Ingeniería en Ciberseguridad','Ingeniería en Informática','Ingeniería Civil en Computación','Ingeniería en Redes y Telecomunicaciones','Ingeniería en Informática'],
 'Salud': ['Enfermería','Kinesiología','Nutrición y Dietética','Técnico en Enfermería','Terapia Ocupacional','Tecnología Médica','Fonoaudiología','Técnico en Odontología','Tecnología Médica','Enfermería'],
 'Administración y finanzas': ['Auditoría y Contabilidad','Ingeniería Comercial','Administración de Empresas','Auditoría y Contabilidad','Ingeniería Comercial','Auditoría y Contabilidad','Ingeniería Comercial','Ingeniería en Recursos Humanos','Ingeniería Comercial','Administración de Empresas'],
 'Diseño y comunicación': ['Diseño Gráfico','Diseño Gráfico','Publicidad','Periodismo','Comunicación Audiovisual','Comunicación Audiovisual','Diseño Gráfico','Periodismo','Artes Visuales','Ingeniería en Marketing'],
 'Educación': ['Educación Parvularia','Pedagogía en Matemáticas','Pedagogía en Lenguaje','Educación Diferencial','Pedagogía en Inglés','Pedagogía en Educación Básica','Pedagogía en Biología y Ciencias Naturales','Bibliotecología','Pedagogía en Artes','Pedagogía en Educación Básica'],
 'Ingeniería y construcción': ['Ingeniería en Construcción','Ingeniería Civil','Técnico en Construcción','Arquitectura','Construcción Civil','Ingeniería en Electricidad','Ingeniería Mecánica','Ingeniería en Construcción','Arquitectura','Construcción Civil'],
 'Logística y operaciones': ['Ingeniería en Logística','Ingeniería en Comercio Exterior','Técnico en Logística','Ingeniería en Logística','Ingeniería en Logística','Técnico en Logística','Ingeniería Industrial','Técnico en Logística','Ingeniería en Comercio Exterior','Ingeniería Industrial'],
 'Turismo y gastronomía': ['Turismo y Hotelería','Técnico en Turismo','Gastronomía','Técnico en Gastronomía','Turismo y Hotelería','Turismo y Hotelería','Turismo y Hotelería','Técnico en Turismo','Turismo y Hotelería','Gastronomía'],
 'Ciencias sociales': ['Psicología','Trabajo Social','Sociología','Derecho','Psicología','Trabajo Social','Trabajo Social','Sociología','Antropología','Trabajo Social'],
 'Medioambiente y agro': ['Ingeniería Ambiental','Agronomía','Ingeniería Ambiental','Ingeniería Forestal','Medicina Veterinaria','Ingeniería Ambiental','Biología','Ingeniería Ambiental','Agronomía','Ingeniería Ambiental'],
}

SECTORS = ['Desarrollo de software','Salud y atención médica','Contabilidad y auditoría',
           'Diseño','Educación escolar','Ingeniería y consultoría técnica',
           'Logística y almacenamiento','Turismo y agencias de viaje',
           'Asistencia social y cuidados','Ingeniería y consultoría técnica']
TASKS = {
 'Tecnología': 'Implementar mejoras, revisar código y documentar pruebas con el equipo técnico.',
 'Salud': 'Apoyar la atención de personas, registrar intervenciones y coordinar el seguimiento con el equipo clínico, dentro de las atribuciones del cargo.',
 'Administración y finanzas': 'Revisar documentos, actualizar registros y preparar reportes de gestión con supervisión.',
 'Diseño y comunicación': 'Preparar propuestas, producir contenidos y aplicar mejoras a partir de revisiones del equipo.',
 'Educación': 'Preparar actividades y materiales, acompañar el aprendizaje y registrar avances de los estudiantes.',
 'Ingeniería y construcción': 'Revisar antecedentes técnicos, apoyar la planificación y documentar controles de calidad y seguridad.',
 'Logística y operaciones': 'Actualizar inventarios, coordinar despachos y proponer mejoras a los procesos operativos.',
 'Turismo y gastronomía': 'Preparar el servicio, atender requerimientos y aplicar los procedimientos de calidad de la especialidad.',
 'Ciencias sociales': 'Recopilar antecedentes, apoyar intervenciones y elaborar informes respetando la confidencialidad.',
 'Medioambiente y agro': 'Apoyar el trabajo de terreno, registrar observaciones y preparar reportes técnicos de seguimiento.',
}
DEMO_PASSWORD = 'contraseña'
COMPANY_DESCRIPTION = 'Empresa ficticia. Datos para demostración académica.'
SCHEMA_VERSION = '0006_cierre_convocatorias'


def rut_for(index):
    body = str(76000000 + index)
    total = sum(int(n) * (2 + i % 6) for i, n in enumerate(reversed(body)))
    return body + '-' + '0123456789K0'[11 - total % 11]


def questions_for(index):
    kind = index % 5
    if kind == 0:
        return []
    if kind == 1:
        return [{'id':'resumen','etiqueta':'¿Qué aprendizaje aportarías al cargo?','tipo':'texto','obligatoria':True,'opciones':[]}]
    if kind == 2:
        return [{'id':'proyecto','etiqueta':'Describe un proyecto académico o personal relacionado.','tipo':'parrafo','obligatoria':False,'opciones':[]}]
    if kind == 3:
        return [{'id':'disponibilidad','etiqueta':'¿Cuándo podrías incorporarte?','tipo':'seleccion','obligatoria':True,
                 'opciones':['Inmediatamente','En dos semanas','En un mes']}]
    return [{'id':'capacidades','etiqueta':'¿Qué capacidades has desarrollado en tus proyectos?','tipo':'seleccion_multiple','obligatoria':True,
             'opciones':['Trabajo en equipo','Comunicación','Organización','Herramientas digitales']},
            {'id':'proyectos','etiqueta':'¿Cuántos proyectos académicos o personales has realizado?','tipo':'numero','obligatoria':False,'opciones':[]}]


def jobs():
    cities = ['Santiago','Valparaíso','Concepción','Temuco','La Serena','Puerto Montt','Rancagua','Antofagasta','Talca','Valdivia']
    items = []
    for area_index, (area, (company, titles, requirements)) in enumerate(CATALOG.items()):
        for index, title in enumerate(titles):
            mode = ['remoto','hibrido','presencial'][index % 3] if area in ('Tecnología','Diseño y comunicación','Administración y finanzas') else 'presencial'
            accessible = index % 3 != 2
            conditions = 'Sueldo fijo mensual bruto en CLP. Jornada de 40 horas semanales. Contrato inicial de tres meses con evaluación de continuidad. Inducción y acompañamiento profesional.'
            conditions += {'remoto':' Trabajo a distancia, con equipo de trabajo proporcionado.',
                           'hibrido':' Dos días en oficina y tres a distancia por semana.',
                           'presencial':' Trabajo en dependencias de la empresa; ubicación indicada en la oferta.'}[mode]
            if accessible:
                conditions += ' Se contemplan entrevista accesible y ajustes de herramientas o del puesto, a coordinar según necesidades.'
            items.append({'demo_clave':f'branchit-demo-v2-{area_index:02}-{index:02}',
                'empresa':f'DEMO · {company}', 'categoria':area, 'titulo':title,
                'descripcion':f'Oferta demo: no es una vacante real. Cargo de {title.lower()} en {company}, para una primera experiencia profesional supervisada.',
                'funciones':f'Desempeñar las tareas de {title.lower()}. {TASKS[area]}',
                'sueldo':750000 + area_index * 25000 + index * 50000,
                'perfiles_deseados':[PROFILES[area][index]],
                'condiciones_laborales':conditions,'adaptada_discapacidad':accessible,
                'requisitos':requirements + ' Se aceptan proyectos académicos y prácticas; no se exige experiencia laboral previa.',
                'ubicacion':cities[index], 'modalidad':mode, 'preguntas':questions_for(index)})
    return items


def company_accounts():
    return [{'empresa':f'DEMO · {company}', 'correo':f'seed.branchit.v1.{index}@example.com',
             'contraseña':DEMO_PASSWORD,'categoria':area,'publicaciones':10,
             'rut':rut_for(index),'telefono':f'+569{70000000 + index}',
             'fecha_identidad':f'2020-{index+1:02}-01','giro':SECTORS[index]}
            for index,(area,(company,_,_)) in enumerate(CATALOG.items())]


def validated_data():
    from app.schemas import RegistroEmpresa, OfertaEmpleoCreate
    accounts = company_accounts()
    for account in accounts:
        RegistroEmpresa.model_validate({'email':account['correo'],'password':account['contraseña'],
            'nombre_empresa':account['empresa'],'rubro':account['giro'],'rut':account['rut'],
            'telefono':account['telefono'],'fecha_identidad':account['fecha_identidad']})
    for item in jobs():
        OfertaEmpleoCreate.model_validate({k:v for k,v in item.items() if k not in ('empresa','demo_clave')})
    return accounts


def seed(db):
    from datetime import date
    import secrets
    from app.models import Usuario, PerfilEmpresa, OfertaEmpleo, TipoUsuario
    from app.security import hash_password, verify_password
    accounts = validated_data()
    created = 0
    for account in accounts:
        user = db.query(Usuario).filter_by(email=account['correo']).first()
        if user:
            profile = db.query(PerfilEmpresa).filter_by(usuario_id=user.id).first()
            if (user.tipo != TipoUsuario.empresa or not profile or profile.nombre_empresa != account['empresa']
                    or profile.rubro != account['giro'] or profile.descripcion != COMPANY_DESCRIPTION
                    or user.rut != account['rut']):
                raise RuntimeError('La cuenta demo ya existe con otra configuración. Usa el reinicio explícito o revisa el conflicto; no se sobrescribe.')
            if not verify_password(DEMO_PASSWORD,user.password_hash):
                user.password_hash = hash_password(DEMO_PASSWORD)
                user.token_version += 1
            user.activo = True
        else:
            user = Usuario(email=account['correo'],password_hash=hash_password(DEMO_PASSWORD),tipo=TipoUsuario.empresa,
                rut=account['rut'],telefono=account['telefono'],fecha_identidad=date.fromisoformat(account['fecha_identidad']),
                token_version=secrets.randbelow(2147483646)+1,activo=True)
            db.add(user); db.flush()
            db.add(PerfilEmpresa(usuario_id=user.id,nombre_empresa=account['empresa'],rubro=account['giro'],descripcion=COMPANY_DESCRIPTION))
            db.flush()
        profile = db.query(PerfilEmpresa).filter_by(usuario_id=user.id).one()
        for item in (j for j in jobs() if j['empresa'] == account['empresa']):
            if db.query(OfertaEmpleo.id).filter_by(demo_clave=item['demo_clave']).first():
                continue
            db.add(OfertaEmpleo(empresa_id=profile.id,**{k:v for k,v in item.items() if k != 'empresa'}))
            created += 1
    db.flush()
    return created


def graduate_snapshot(db):
    from app.models import Usuario, PerfilEgresado, ArchivoPortfolio, TipoUsuario
    from sqlalchemy import select
    users = select(Usuario.id).where(Usuario.tipo == TipoUsuario.egresado)
    return {table.name:[dict(row._mapping) for row in db.execute(select(table).where(condition).order_by(table.c.id))]
            for table,condition in [(Usuario.__table__,Usuario.tipo == TipoUsuario.egresado),
                (PerfilEgresado.__table__,PerfilEgresado.usuario_id.in_(users)),
                (ArchivoPortfolio.__table__,ArchivoPortfolio.usuario_id.in_(users))]}


def reset_companies(db, backup_path):
    """Caller owns the transaction. All graduates are preserved, IDs are not reset."""
    from app.models import Usuario, PerfilEmpresa, OfertaEmpleo, Postulacion, ArchivoPortfolio, TipoUsuario
    from sqlalchemy import select, text
    validated_data()
    if db.bind.dialect.name == 'postgresql':
        db.execute(text('LOCK TABLE usuarios, perfiles_egresado, perfiles_empresa, ofertas_empleo, postulaciones, archivos_portfolio IN SHARE ROW EXCLUSIVE MODE'))
    if db.execute(text('SELECT version_num FROM alembic_version')).scalar() != SCHEMA_VERSION:
        raise RuntimeError('Ejecuta alembic upgrade head antes del reinicio.')
    before = graduate_snapshot(db)
    company_ids = select(Usuario.id).where(Usuario.tipo == TipoUsuario.empresa)
    rows = {table.name:[dict(row._mapping) for row in db.execute(select(table).where(condition))]
            for table,condition in [(Usuario.__table__,Usuario.tipo == TipoUsuario.empresa),
                (PerfilEmpresa.__table__,True),(OfertaEmpleo.__table__,True),(Postulacion.__table__,True),
                (ArchivoPortfolio.__table__,ArchivoPortfolio.usuario_id.in_(company_ids))]}
    backup_path = Path(backup_path)
    backup_path.parent.mkdir(parents=True,exist_ok=True)
    with backup_path.open('x',encoding='utf-8') as output:
        json.dump({'schema':SCHEMA_VERSION,'tables':rows},output,ensure_ascii=False,default=str,indent=2)
    db.query(Postulacion).delete(synchronize_session='fetch')
    db.query(OfertaEmpleo).delete(synchronize_session='fetch')
    db.query(PerfilEmpresa).delete(synchronize_session='fetch')
    db.query(ArchivoPortfolio).filter(ArchivoPortfolio.usuario_id.in_(company_ids)).delete(synchronize_session='fetch')
    db.query(Usuario).filter_by(tipo=TipoUsuario.empresa).delete(synchronize_session='fetch')
    db.flush()
    inserted = seed(db)
    if graduate_snapshot(db) != before or inserted != 100 or db.query(Postulacion).count() != 0:
        raise RuntimeError('La verificación del reinicio falló; revierte la transacción.')
    return {'empresas_eliminadas':len(rows['usuarios']),'ofertas_eliminadas':len(rows['ofertas_empleo']),
            'postulaciones_eliminadas':len(rows['postulaciones']),'empresas_creadas':10,'ofertas_creadas':inserted}


def export_accounts(path):
    import csv
    path = Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    accounts = company_accounts()
    with path.open('w',encoding='utf-8-sig',newline='') as output:
        writer = csv.DictWriter(output,fieldnames=list(accounts[0]))
        writer.writeheader(); writer.writerows(accounts)


def reset_sql(backup_schema, expected_counts=None):
    """Equivalent atomic reset for Neon SQL Editor, with a private SQL backup."""
    import re
    import secrets
    from app.security import hash_password
    if not re.fullmatch(r'branchit_backup_[a-z0-9_]{1,40}',backup_schema):
        raise ValueError('Nombre de respaldo no válido.')
    validated_data()
    def literal(value):
        if value is None: return 'NULL'
        if isinstance(value,bool): return 'true' if value else 'false'
        if isinstance(value,int): return str(value)
        if isinstance(value,(list,dict)): return literal(json.dumps(value,ensure_ascii=False))+'::json'
        return "'" + str(value).replace("'","''") + "'"
    snapshot = """jsonb_build_object(
        'usuarios',(SELECT jsonb_agg(to_jsonb(u) ORDER BY id) FROM usuarios u WHERE tipo='egresado'),
        'perfiles',(SELECT jsonb_agg(to_jsonb(p) ORDER BY id) FROM perfiles_egresado p),
        'archivos',(SELECT jsonb_agg(to_jsonb(a) ORDER BY a.id) FROM archivos_portfolio a JOIN usuarios u ON a.usuario_id=u.id WHERE u.tipo='egresado'))"""
    sql = ["DO $branchit_reset$", 'DECLARE uid integer; pid integer; graduates_before jsonb; graduates_after jsonb;', 'BEGIN',
        'LOCK TABLE usuarios, perfiles_egresado, perfiles_empresa, ofertas_empleo, postulaciones, archivos_portfolio IN SHARE ROW EXCLUSIVE MODE;',
        f"IF (SELECT version_num FROM alembic_version) IS DISTINCT FROM '{SCHEMA_VERSION}' THEN RAISE EXCEPTION 'Esquema inesperado: ejecuta alembic upgrade head'; END IF;"]
    checks = {'empresas':"SELECT count(*) FROM usuarios WHERE tipo='empresa'",
              'egresados':"SELECT count(*) FROM usuarios WHERE tipo='egresado'",
              'ofertas':'SELECT count(*) FROM ofertas_empleo', 'postulaciones':'SELECT count(*) FROM postulaciones',
              'archivos_empresa':"SELECT count(*) FROM archivos_portfolio a JOIN usuarios u ON u.id=a.usuario_id WHERE u.tipo='empresa'"}
    for key, count in (expected_counts or {}).items():
        if key not in checks or type(count) is not int or count < 0:
            raise ValueError('Verificación de cantidades no válida.')
        sql.append(f"IF ({checks[key]}) <> {count} THEN RAISE EXCEPTION 'Cambió la cantidad de {key}; revisar antes de reiniciar'; END IF;")
    sql.extend([
        f'SELECT {snapshot} INTO graduates_before;',
        f'CREATE SCHEMA {backup_schema};',
        f"CREATE TABLE {backup_schema}.usuarios AS SELECT * FROM usuarios WHERE tipo='empresa';",
        f'CREATE TABLE {backup_schema}.perfiles_empresa AS TABLE perfiles_empresa;',
        f'CREATE TABLE {backup_schema}.ofertas_empleo AS TABLE ofertas_empleo;',
        f'CREATE TABLE {backup_schema}.postulaciones AS TABLE postulaciones;',
        f"CREATE TABLE {backup_schema}.archivos_portfolio AS SELECT a.* FROM archivos_portfolio a JOIN usuarios u ON u.id=a.usuario_id WHERE u.tipo='empresa';",
        'DELETE FROM postulaciones;', 'DELETE FROM ofertas_empleo;', 'DELETE FROM perfiles_empresa;',
        "DELETE FROM archivos_portfolio WHERE usuario_id IN (SELECT id FROM usuarios WHERE tipo='empresa');",
        "DELETE FROM usuarios WHERE tipo='empresa';"])
    password_hash = hash_password(DEMO_PASSWORD)
    for account in company_accounts():
        fields = ['email','password_hash','tipo','fecha_registro','activo','token_version','rut','telefono','fecha_identidad']
        values = [account['correo'],password_hash,'empresa',None,True,secrets.randbelow(2147483646)+1,account['rut'],account['telefono'],account['fecha_identidad']]
        encoded = [literal(value) if field != 'fecha_registro' else 'NOW()' for field,value in zip(fields,values)]
        sql.append(f"INSERT INTO usuarios ({','.join(fields)}) VALUES ({','.join(encoded)}) RETURNING id INTO uid;")
        sql.append('INSERT INTO perfiles_empresa (usuario_id,nombre_empresa,rubro,descripcion) VALUES (uid,'+
                   ','.join(literal(value) for value in (account['empresa'],account['giro'],COMPANY_DESCRIPTION))+') RETURNING id INTO pid;')
        for item in (j for j in jobs() if j['empresa'] == account['empresa']):
            values = {k:v for k,v in item.items() if k != 'empresa'}
            sql.append('INSERT INTO ofertas_empleo (empresa_id,'+','.join(values)+',formulario_version,activa,fecha_publicacion) VALUES (pid,'+
                       ','.join(literal(value) for value in values.values())+',1,true,NOW());')
    sql.extend([f'SELECT {snapshot} INTO graduates_after;',
        "IF graduates_before IS DISTINCT FROM graduates_after THEN RAISE EXCEPTION 'Se alteraron datos de egresados: se revierte todo'; END IF;",
        "IF (SELECT count(*) FROM usuarios WHERE tipo='empresa') <> 10 OR (SELECT count(*) FROM perfiles_empresa) <> 10 OR (SELECT count(*) FROM ofertas_empleo) <> 100 OR (SELECT count(*) FROM postulaciones) <> 0 THEN RAISE EXCEPTION 'Cantidades inesperadas: se revierte todo'; END IF;",
        "IF EXISTS (SELECT 1 FROM ofertas_empleo WHERE sueldo IS NULL OR sueldo <= 0 OR funciones IS NULL OR perfiles_deseados IS NULL OR condiciones_laborales IS NULL OR adaptada_discapacidad IS NULL OR NOT activa) THEN RAISE EXCEPTION 'Ofertas incompletas: se revierte todo'; END IF;",
        'END $branchit_reset$;'])
    return '\n'.join(sql)+'\n'


def main():
    import argparse
    from datetime import datetime
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply',action='store_true',help='Guardar datos demo sin duplicar ni modificar ofertas existentes.')
    parser.add_argument('--reset-companies',action='store_true',help='Borrar TODAS las empresas, sus ofertas y TODAS las postulaciones antes de crear 10 empresas y 100 ofertas.')
    parser.add_argument('--confirm-reset',choices=['BORRAR_EMPRESAS_Y_POSTULACIONES'])
    parser.add_argument('--backup',type=Path,default=Path(__file__).resolve().parents[2]/'.vercel'/f'backup-empresas-{datetime.now():%Y%m%d-%H%M%S}.json')
    parser.add_argument('--accounts-csv',type=Path,help='Exportar las diez cuentas ficticias de testing.')
    parser.add_argument('--sql',type=Path,help='Guardar SQL de reinicio con respaldo para Neon, sin ejecutarlo.')
    parser.add_argument('--backup-schema',default=f'branchit_backup_{datetime.now():%Y%m%d_%H%M%S}')
    args = parser.parse_args()
    if args.sql and args.apply:
        parser.error('--sql solo prepara el archivo; no se combina con --apply.')
    if args.reset_companies and (not args.apply or not args.confirm_reset):
        parser.error('El reinicio requiere --apply y --confirm-reset BORRAR_EMPRESAS_Y_POSTULACIONES.')
    if args.sql:
        args.sql.parent.mkdir(parents=True,exist_ok=True)
        args.sql.write_text(reset_sql(args.backup_schema),encoding='utf-8')
        print('SQL preparado; no se ejecutó en la BD.')
    elif not args.apply:
        print(json.dumps(jobs(),ensure_ascii=False,indent=2))
        print('\nVista previa: 10 empresas y 100 ofertas. Sin cambios en la BD.',file=sys.stderr)
    else:
        from app.database import SessionLocal
        from app.config import DATABASE_URL
        from urllib.parse import urlsplit
        target = urlsplit(DATABASE_URL)
        print(f'Destino: {target.hostname or "local"}/{target.path.lstrip("/")}',file=sys.stderr)
        with SessionLocal() as db:
            try:
                if args.reset_companies:
                    result = reset_companies(db,args.backup)
                else:
                    count = seed(db)
                    result = {'insertadas':count,'ya_existentes':100-count}
                db.commit()
                print(json.dumps(result,ensure_ascii=False))
            except Exception:
                db.rollback()
                raise
    if args.accounts_csv:
        export_accounts(args.accounts_csv)


if __name__ == '__main__':
    main()
