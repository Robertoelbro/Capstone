from decimal import Decimal, InvalidOperation
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..encryption import encrypt_data, decrypt_data
from ..security import current_user

router = APIRouter(prefix='/api/employment', tags=['postulaciones'])


def role(user, expected):
    if user.tipo.value != expected:
        raise HTTPException(403, 'Tu tipo de cuenta no puede realizar esta acción.')


def serialize(item):
    return {'id': item.id, 'oferta_id': item.oferta_id,
            'titulo': item.oferta.titulo, 'nombre_empresa': item.oferta.empresa.nombre_empresa,
            'fecha_postulacion': item.fecha_postulacion, 'oferta_activa': item.oferta.activa,
            'estado': 'recibida', 'datos': decrypt_data(item.datos_cifrados)}


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
    answers = {key: value.strip() for key, value in data.respuestas.items()}
    for question in job.preguntas:
        answer = answers.get(question['id'], '')
        if question['obligatoria'] and not answer:
            raise HTTPException(422, f"Responde la pregunta: {question['etiqueta']}")
        if answer and question['tipo'] == 'seleccion' and answer not in question['opciones']:
            raise HTTPException(422, 'Selecciona una opción válida.')
        if answer and question['tipo'] == 'numero':
            try:
                if not Decimal(answer).is_finite():
                    raise InvalidOperation
            except InvalidOperation:
                raise HTTPException(422, 'La respuesta numérica no es válida.')
    payload = {'nombre': profile.nombre, 'apellido': profile.apellido, 'email': user.email,
               'carrera': profile.carrera, 'presentacion': profile.presentacion,
               'telefono': data.telefono, 'cv_url': data.cv_url, 'mensaje': data.mensaje,
               'preguntas': job.preguntas, 'respuestas': answers, 'consentimiento': True}
    item = models.Postulacion(oferta_id=job.id, egresado_id=profile.id, datos_cifrados=encrypt_data(payload))
    db.add(item)
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
    return [serialize(item) for item in db.query(models.Postulacion).filter_by(oferta_id=job.id)
            .order_by(models.Postulacion.fecha_postulacion.desc()).all()]
