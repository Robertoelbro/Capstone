from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models
from ..database import get_db
from ..security import current_user

router = APIRouter(prefix='/notifications', tags=['notificaciones'])


def notify_job_change(db, job, active):
    """Only public call status is sent; candidate selection stays private."""
    for application in job.postulaciones:
        db.add(models.Notificacion(
            usuario_id=application.egresado.usuario_id,
            mensaje=f"La convocatoria «{job.titulo}» {'se reabrió' if active else 'se cerró'}.",
            destino='/mis-postulaciones'))


@router.get('')
def inbox(user=Depends(current_user), db: Session = Depends(get_db)):
    query = db.query(models.Notificacion).filter_by(usuario_id=user.id)
    unread = query.filter_by(leida=False).count()
    items = query.order_by(models.Notificacion.id.desc()).limit(50).all()
    return {'sin_leer': unread, 'items': [
        {'id': n.id, 'mensaje': n.mensaje, 'destino': n.destino,
         'leida': n.leida, 'creada': n.creada} for n in items]}


@router.put('/read-all', status_code=204)
def read_all(user=Depends(current_user), db: Session = Depends(get_db)):
    db.query(models.Notificacion).filter_by(usuario_id=user.id, leida=False).update({'leida': True})
    db.commit()


@router.put('/{notification_id}/read', status_code=204)
def read_one(notification_id: int, user=Depends(current_user), db: Session = Depends(get_db)):
    item = db.query(models.Notificacion).filter_by(id=notification_id, usuario_id=user.id).first()
    if not item:
        raise HTTPException(404, 'Notificación no encontrada.')
    item.leida = True
    db.commit()
