"""Employment declarations, recruiter hiring and private supporting documents."""
from datetime import date, datetime
from typing import Literal
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException
from pydantic import Field, model_validator
from sqlalchemy.orm import Session

from ..database import get_db
from ..encryption import decrypt_data, encrypt_data
from ..models import ArchivoPortfolio, Postulacion, SeguimientoLaboral, Usuario
from ..portfolio_schemas import AssetId
from ..schemas import InputModel
from ..security import current_user

router = APIRouter(prefix='/employment', tags=['seguimiento laboral'])


def today():
    return datetime.now(ZoneInfo('America/Santiago')).date()


def anniversary(start):
    try:
        return start.replace(year=start.year + 1)
    except ValueError:
        return start.replace(year=start.year + 1, day=28)


class EmploymentInput(InputModel):
    situacion: Literal['buscando', 'trabajando']
    busqueda_activa: bool
    empresa: str | None = Field(default=None, max_length=150)
    cargo: str | None = Field(default=None, max_length=150)
    fecha_inicio: date | None = None
    postulacion_id: int | None = Field(default=None, gt=0)

    @model_validator(mode='after')
    def validate_employment(self):
        if self.fecha_inicio and self.fecha_inicio > today():
            raise ValueError('La fecha de inicio no puede estar en el futuro.')
        if self.situacion == 'buscando' and any((self.empresa, self.cargo, self.fecha_inicio, self.postulacion_id)):
            raise ValueError('Los antecedentes de contratación corresponden a la situación trabajando.')
        if self.situacion == 'trabajando':
            if not self.fecha_inicio:
                raise ValueError('Indica la fecha de inicio del empleo.')
            self.busqueda_activa = False
        return self


class ReleaseInput(InputModel):
    archivo_id: AssetId
    fecha_inicio: date | None = None
    fecha_fin: date
    motivo: Literal['renuncia', 'despido']

    @model_validator(mode='after')
    def dates(self):
        if self.fecha_fin > today() or (self.fecha_inicio and self.fecha_inicio > self.fecha_fin):
            raise ValueError('Revisa las fechas: el término no puede estar en el futuro ni antes del inicio.')
        return self


def graduate_only(user):
    if user.tipo.value != 'egresado':
        raise HTTPException(403, 'El seguimiento laboral es exclusivo del egresado.')


def lock_account(db, user):
    db.query(Usuario).filter_by(id=user.id).populate_existing().with_for_update().one()
    if not user.activo:
        raise HTTPException(401, 'La cuenta está desactivada.')


def state(item):
    data = decrypt_data(item.datos_cifrados) if item else {}
    situation = item.situacion if item else 'buscando'
    active = item.busqueda_activa if item else True
    limit = bool(item and item.limite_experiencia)
    reason = 'limite_experiencia' if limit else 'trabajando' if situation == 'trabajando' else 'busqueda_pausada' if not active else None
    return {'situacion': situation, 'busqueda_activa': active and not limit,
            **{key: data.get(key) for key in ('empresa', 'cargo', 'fecha_inicio', 'postulacion_id',
                                             'fecha_fin', 'finiquito_id', 'origen')},
            'actualizado': item.actualizado if item else None, 'puede_postular': reason is None,
            'requiere_finiquito': situation == 'trabajando', 'limite_experiencia': limit,
            'motivo_bloqueo': reason}


def document_referenced(db, user_id, asset_id):
    item = db.query(SeguimientoLaboral).filter_by(usuario_id=user_id).first()
    if not item:
        return False
    data = decrypt_data(item.datos_cifrados)
    return asset_id == data.get('finiquito_id') or any(
        period.get('finiquito_id') == asset_id for period in data.get('historial_empleos', []))


def record_hiring(db, selected, start):
    """Caller locks the graduate's account before the job, as apply does."""
    user_id = selected.egresado.usuario_id
    item = db.query(SeguimientoLaboral).filter_by(usuario_id=user_id).first()
    data = decrypt_data(item.datos_cifrados) if item else {}
    if (data.get('postulacion_id') == selected.id or any(
            period.get('postulacion_id') == selected.id for period in data.get('historial_empleos', []))):
        return
    if item and item.situacion == 'trabajando':
        raise HTTPException(409, 'El candidato ya tiene un empleo vigente registrado. No se reemplazará.')
    if not item:
        item = SeguimientoLaboral(usuario_id=user_id, limite_experiencia=False)
    item.situacion = 'trabajando'
    item.busqueda_activa = False
    item.datos_cifrados = encrypt_data({
        'empresa': selected.oferta.empresa.nombre_empresa, 'cargo': selected.oferta.titulo,
        'fecha_inicio': start.isoformat(), 'postulacion_id': selected.id, 'origen': 'empresa',
        'historial_empleos': data.get('historial_empleos', [])})
    item.actualizado = datetime.utcnow()
    db.add(item)


@router.get('/me')
def employment_state(user=Depends(current_user), db: Session = Depends(get_db)):
    graduate_only(user)
    return state(db.query(SeguimientoLaboral).filter_by(usuario_id=user.id).first())


@router.put('/me')
def save_employment(data: EmploymentInput, user=Depends(current_user), db: Session = Depends(get_db)):
    graduate_only(user)
    lock_account(db, user)
    item = db.query(SeguimientoLaboral).filter_by(usuario_id=user.id).first()
    existing = decrypt_data(item.datos_cifrados) if item else {}
    if item and item.situacion == 'trabajando':
        incoming = data.model_dump(mode='json', exclude={'situacion', 'busqueda_activa'})
        if data.situacion != 'trabajando' or any(incoming[k] != existing.get(k) for k in incoming):
            raise HTTPException(409, 'Para terminar el empleo debes presentar tu finiquito PDF en el seguimiento laboral.')
        return state(item)
    if item and item.limite_experiencia and data.busqueda_activa:
        raise HTTPException(409, 'Alcanzaste un año en un empleo registrado. Las nuevas postulaciones quedan deshabilitadas permanentemente.')
    if data.postulacion_id is not None:
        application = db.query(Postulacion).filter_by(
            id=data.postulacion_id, egresado_id=user.perfil_egresado.id).first()
        if not application:
            raise HTTPException(422, 'Selecciona una de tus propias postulaciones.')
    if item is None:
        item = SeguimientoLaboral(usuario_id=user.id, limite_experiencia=False)
        db.add(item)
    item.situacion = data.situacion
    item.busqueda_activa = data.busqueda_activa and not item.limite_experiencia
    if data.situacion == 'trabajando':
        payload = data.model_dump(mode='json', exclude={'situacion', 'busqueda_activa'})
        payload.update(origen='declarado', historial_empleos=existing.get('historial_empleos', []))
    else:
        payload = existing
    item.datos_cifrados = encrypt_data(payload)
    item.actualizado = datetime.utcnow()
    db.commit()
    db.refresh(item)
    return state(item)


@router.post('/release')
def release_employment(data: ReleaseInput, user=Depends(current_user), db: Session = Depends(get_db)):
    graduate_only(user)
    lock_account(db, user)
    item = db.query(SeguimientoLaboral).filter_by(usuario_id=user.id).first()
    if not item or item.situacion != 'trabajando':
        raise HTTPException(409, 'No tienes un empleo vigente que finalizar.')
    existing = decrypt_data(item.datos_cifrados)
    start = date.fromisoformat(existing['fecha_inicio']) if existing.get('fecha_inicio') else data.fecha_inicio
    if not start:
        raise HTTPException(422, 'Este registro antiguo no tiene fecha de inicio. Indícala para calcular la duración.')
    if data.fecha_inicio and data.fecha_inicio != start:
        raise HTTPException(422, 'La fecha de inicio registrada no puede modificarse mediante el finiquito.')
    if start > data.fecha_fin:
        raise HTTPException(422, 'La fecha de término no puede ser anterior al inicio del empleo.')
    asset = db.query(ArchivoPortfolio).filter_by(id=data.archivo_id).with_for_update().first()
    if not asset or asset.usuario_id != user.id or asset.tipo != 'finiquito' or not asset.verificado or asset.mime != 'application/pdf' or asset.tamano > 5 * 1024 * 1024:
        raise HTTPException(422, 'Selecciona tu propio finiquito PDF verificado de hasta 5 MB.')
    if document_referenced(db, user.id, asset.id):
        raise HTTPException(409, 'Este documento ya respalda un empleo terminado. Sube el finiquito correspondiente a este empleo.')
    period = {key: existing.get(key) for key in ('empresa', 'cargo', 'postulacion_id', 'origen')}
    period.update(fecha_inicio=start.isoformat(), fecha_fin=data.fecha_fin.isoformat(),
                  finiquito_id=asset.id, motivo=data.motivo)
    existing.update(period)
    existing['historial_empleos'] = [*existing.get('historial_empleos', []), period]
    item.limite_experiencia = item.limite_experiencia or data.fecha_fin >= anniversary(start)
    item.situacion = 'buscando'
    item.busqueda_activa = not item.limite_experiencia
    item.datos_cifrados = encrypt_data(existing)
    item.actualizado = datetime.utcnow()
    db.commit()
    db.refresh(item)
    return state(item)
