from decimal import Decimal, InvalidOperation
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..encryption import encrypt_data, decrypt_data
from ..security import current_user
from .notifications import notify_job_change
from ..applicant_matching import affinity

router = APIRouter(prefix='/api/employment', tags=['postulaciones'])


def role(user, expected):
    if user.tipo.value != expected:
        raise HTTPException(403, 'Tu tipo de cuenta no puede realizar esta acción.')


def serialize(item, private=False):
    result = {'id': item.id, 'oferta_id': item.oferta_id,
            'titulo': item.oferta.titulo, 'nombre_empresa': item.oferta.empresa.nombre_empresa,
            'fecha_postulacion': item.fecha_postulacion, 'oferta_activa': item.oferta.activa,
            'estado': 'recibida' if item.oferta.activa else 'cerrada', 'datos': decrypt_data(item.datos_cifrados)}
    result['empresa_foto_id'] = item.oferta.empresa.foto_id
    result['empresa_logo_url'] = item.oferta.empresa.logo_url
    if private:
        result['seleccionada'] = item.seleccionada
        profile = item.egresado
        result['portfolio_url'] = f'/p/{profile.usuario_id}' if (profile.portfolio or {}).get('publico') else None
        # New applications keep the declared evidence as a snapshot. Legacy ones
        # use the current profile and identify that fact explicitly.
        portfolio = result['datos'].get('antecedentes_profesionales', profile.portfolio or {})
        result['antecedentes'] = {key: portfolio.get(key, default) for key, default in
            [('habilidades', []), ('proyectos', []), ('certificaciones', []),
             ('experiencia_laboral', []), ('titulo_url', ''), ('disponibilidad', 'Sin definir')]}
        result['antecedentes_actuales'] = 'antecedentes_profesionales' not in result['datos']
        result['afinidad'] = affinity(item.oferta, result['datos'].get('carrera'), portfolio)
    return result


@router.post('/applications', status_code=201)
def apply(data: schemas.PostulacionCreate, user=Depends(current_user), db: Session = Depends(get_db)):
    role(user, 'egresado')
    # Serialize closing/editing the offer with submissions on PostgreSQL.
    job = db.query(models.OfertaEmpleo).filter_by(id=data.oferta_id).with_for_update().first()
    if not job:
        raise HTTPException(404, 'Oferta no encontrada.')
    if not job.activa:
        raise HTTPException(409, 'La oferta ya no recibe postulaciones.')
    if data.formulario_version != job.formulario_version:
        raise HTTPException(409, 'La empresa actualizó el formulario. Recarga la página antes de postular.')
    profile = user.perfil_egresado
    if not profile:
        raise HTTPException(409, 'Completa tu perfil antes de postular.')
    if db.query(models.Postulacion).filter_by(oferta_id=job.id, egresado_id=profile.id).first():
        raise HTTPException(409, 'Ya postulaste a esta oferta.')
    expected = {q['id'] for q in job.preguntas}
    if set(data.respuestas) - expected:
        raise HTTPException(422, 'El formulario contiene respuestas a preguntas no solicitadas.')
    answers = {key: [item.strip() for item in value] if isinstance(value, list) else value.strip() for key, value in data.respuestas.items()}
    for question in job.preguntas:
        answer = answers.get(question['id'], '')
        multiple = question['tipo'] == 'seleccion_multiple'
        if multiple and question['id'] not in answers:
            answer = []
        if isinstance(answer, list) != multiple:
            raise HTTPException(422, 'El tipo de respuesta no corresponde a la pregunta.')
        if multiple and (len(set(answer)) != len(answer) or any(item not in question['opciones'] for item in answer)):
            raise HTTPException(422, 'Selecciona opciones válidas y sin repetir.')
        if question['tipo'] == 'texto' and len(answer) > 200:
            raise HTTPException(422, 'El texto corto admite hasta 200 caracteres.')
        if question['obligatoria'] and not answer:
            raise HTTPException(422, f"Responde la pregunta: {question['etiqueta']}")
        if answer and question['tipo'] == 'seleccion' and answer not in question['opciones']:
            raise HTTPException(422, 'Selecciona una opción válida.')
        if answer and question['tipo'] == 'numero':
            try:
                import re
                if not re.fullmatch(r'-?[0-9]+([.,][0-9]+)?', answer) or not Decimal(answer.replace(',', '.')).is_finite():
                    raise InvalidOperation
            except InvalidOperation:
                raise HTTPException(422, 'La respuesta numérica no es válida.')
    payload = {'nombre': profile.nombre, 'apellido': profile.apellido, 'email': user.email,
               'carrera': profile.carrera, 'presentacion': profile.presentacion,
               'telefono': data.telefono, 'cv_url': data.cv_url, 'mensaje': data.mensaje,
               'preguntas': job.preguntas, 'respuestas': answers, 'consentimiento': True,
               'antecedentes_profesionales': {k: v for k, v in (profile.portfolio or {}).items()
                   if k in ('habilidades', 'proyectos', 'certificaciones', 'experiencia_laboral', 'titulo_url', 'disponibilidad')}}
    item = models.Postulacion(oferta_id=job.id, egresado_id=profile.id, datos_cifrados=encrypt_data(payload))
    db.add(item)
    db.add(models.Notificacion(usuario_id=job.empresa.usuario_id,
        mensaje=f'Recibiste una nueva postulación para «{job.titulo}».',
        destino=f'/ofertas-empresa/{job.id}/postulaciones'))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, 'Ya existe una postulación para esta oferta.')
    db.refresh(item)
    return serialize(item)


@router.get('/applications/me')
def my_applications(user=Depends(current_user), db: Session = Depends(get_db)):
    role(user, 'egresado')
    items = (db.query(models.Postulacion).join(models.PerfilEgresado)
             .filter(models.PerfilEgresado.usuario_id == user.id)
             .order_by(models.Postulacion.fecha_postulacion.desc()).all())
    return [serialize(item) for item in items]


@router.get('/jobs/{job_id}/applications')
def applicants(job_id: int, user=Depends(current_user), db: Session = Depends(get_db)):
    role(user, 'empresa')
    job = (db.query(models.OfertaEmpleo).join(models.PerfilEmpresa)
           .filter(models.OfertaEmpleo.id == job_id, models.PerfilEmpresa.usuario_id == user.id).first())
    if not job:
        raise HTTPException(404, 'Oferta no encontrada.')
    results = [serialize(item, private=True) for item in db.query(models.Postulacion).filter_by(oferta_id=job.id)
            .order_by(models.Postulacion.fecha_postulacion.asc(), models.Postulacion.id.asc()).all()]
    results.sort(key=lambda item: (-item['afinidad']['puntos'], -len(item['afinidad']['coincidencias'])))
    for position, item in enumerate(results):
        item['posicion'] = position + 1
        item['destacado'] = position < 10 and item['afinidad']['puntos'] > 0
    return results


@router.put('/jobs/{job_id}/closure')
def close_call(job_id: int, data: schemas.CierreConvocatoria, user=Depends(current_user), db: Session = Depends(get_db)):
    role(user, 'empresa')
    job = (db.query(models.OfertaEmpleo).join(models.PerfilEmpresa)
           .filter(models.OfertaEmpleo.id == job_id, models.PerfilEmpresa.usuario_id == user.id)
           .with_for_update(of=models.OfertaEmpleo).first())
    if not job:
        raise HTTPException(404, 'Oferta no encontrada.')
    selected = None
    if data.postulacion_id is not None:
        selected = db.query(models.Postulacion).filter_by(id=data.postulacion_id, oferta_id=job.id).first()
        if not selected:
            raise HTTPException(422, 'Selecciona un postulante de esta oferta.')
    db.query(models.Postulacion).filter_by(oferta_id=job.id).update({'seleccionada': False}, synchronize_session='fetch')
    db.flush()
    if selected:
        selected.seleccionada = True
    if job.activa:
        notify_job_change(db, job, False)
    job.activa = False
    db.commit()
    return {'oferta_id': job.id, 'activa': False, 'postulacion_seleccionada_id': data.postulacion_id}
