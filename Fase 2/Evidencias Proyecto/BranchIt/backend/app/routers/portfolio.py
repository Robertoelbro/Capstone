from uuid import uuid4
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Header
import os
import secrets
from sqlalchemy import func
from sqlalchemy.orm import Session
from ..database import get_db
from ..security import current_user, bearer
from ..models import PerfilEgresado, PerfilEmpresa, ArchivoPortfolio, Usuario
from ..portfolio_schemas import Portfolio, MediaReserve, media_references

router = APIRouter(tags=['portafolio'])

def own_profile(user, db):
    if user.tipo.value != 'egresado':
        raise HTTPException(403, 'Solo los egresados tienen portafolio.')
    profile = db.query(PerfilEgresado).filter_by(usuario_id=user.id).first()
    if not profile: raise HTTPException(404, 'Perfil no encontrado.')
    return profile

@router.put('/portfolio/me')
def save_portfolio(data: Portfolio, user=Depends(current_user), db: Session=Depends(get_db)):
    profile = own_profile(user, db)
    payload = data.model_dump()
    for asset_id, kind in media_references(payload):
        asset = db.get(ArchivoPortfolio, asset_id)
        if not asset or not asset.verificado or asset.usuario_id != user.id or asset.tipo != kind:
            raise HTTPException(422, 'Uno de los archivos no corresponde a tu perfil o a este campo.')
    profile.portfolio = payload
    db.commit()
    return payload

@router.get('/portfolio/{user_id}')
def public_portfolio(user_id: int, db: Session=Depends(get_db)):
    profile = db.query(PerfilEgresado).join(Usuario).filter(PerfilEgresado.usuario_id==user_id, Usuario.activo.is_(True)).first()
    if not profile or not (profile.portfolio or {}).get('publico'):
        raise HTTPException(404, 'Este portafolio no está publicado.')
    data = Portfolio.model_validate(profile.portfolio).model_dump()
    if not data['mostrar_email']: data['contacto_email'] = ''
    if not data['mostrar_telefono']: data['contacto_telefono'] = ''
    return {'usuario_id': user_id, 'nombre': profile.nombre, 'apellido': profile.apellido,
            'carrera': profile.carrera, 'anio_egreso': profile.anio_egreso,
            'presentacion': profile.presentacion, 'foto_url': profile.foto_url,
            'linkedin_url': profile.linkedin_url, 'portfolio': data}

@router.post('/media/reserve', status_code=201)
def reserve(data: MediaReserve, user=Depends(current_user), db: Session=Depends(get_db)):
    if user.tipo.value == 'empresa' and data.tipo != 'foto':
        raise HTTPException(403, 'Las empresas pueden subir fotos de perfil.')
    limits = {'foto': (3, ['image/jpeg','image/png','image/webp']),
              'qr': (3, ['image/jpeg','image/png','image/webp']),
              'certificado': (5, ['application/pdf','image/jpeg','image/png','image/webp']),
              'presentacion': (15, ['video/mp4','video/webm']),
              'proyecto': (30, ['video/mp4','video/webm'])}
    size, types = limits[data.tipo]
    if data.mime not in types or data.tamano > size * 1024 * 1024:
        raise HTTPException(422, f'Tipo de archivo no admitido o supera {size} MB.')
    if data.tipo in ('presentacion','proyecto') and (not data.duracion or data.duracion > (60 if data.tipo=='presentacion' else 180)):
        raise HTTPException(422, 'El video excede la duración permitida.')
    # Lock the account to serialize quota reservations across server instances.
    db.query(Usuario).filter_by(id=user.id).with_for_update().first()
    used, count = db.query(func.coalesce(func.sum(ArchivoPortfolio.tamano),0), func.count(ArchivoPortfolio.id)).filter_by(usuario_id=user.id).one()
    if used + data.tamano > 100 * 1024 * 1024 or count >= 40:
        raise HTTPException(409, 'Llegaste al límite de 100 MB o 40 archivos. Elimina archivos sin usar en tu biblioteca.')
    asset_id = uuid4().hex
    ext = {'image/jpeg':'jpg','image/png':'png','image/webp':'webp','application/pdf':'pdf','video/mp4':'mp4','video/webm':'webm'}[data.mime]
    asset = ArchivoPortfolio(id=asset_id, usuario_id=user.id, tipo=data.tipo, nombre=data.nombre,
        mime=data.mime, tamano=data.tamano, duracion=data.duracion,
        pathname=f'portfolios/{user.id}/{asset_id}.{ext}')
    db.add(asset)
    db.commit()
    return {'id': asset.id, 'pathname': asset.pathname}

@router.get('/media/library')
def library(user=Depends(current_user), db: Session=Depends(get_db)):
    return [{'id':a.id,'nombre':a.nombre,'tipo':a.tipo,'tamano':a.tamano}
            for a in db.query(ArchivoPortfolio).filter_by(usuario_id=user.id).order_by(ArchivoPortfolio.creado.desc()).all()]

@router.get('/media/{asset_id}/access')
def media_access(asset_id: str, upload: bool=False, remove: bool=False, credentials=Depends(bearer), db: Session=Depends(get_db)):
    asset = db.get(ArchivoPortfolio, asset_id)
    if not asset: raise HTTPException(404, 'Archivo no encontrado.')
    owner = False
    if credentials:
        try: owner = current_user(credentials, db).id == asset.usuario_id
        except HTTPException: pass
    profile = db.query(PerfilEgresado).join(Usuario).filter(PerfilEgresado.usuario_id==asset.usuario_id, Usuario.activo.is_(True)).first()
    company = db.query(PerfilEmpresa).filter_by(usuario_id=asset.usuario_id).first()
    public = profile and (profile.portfolio or {}).get('publico') and asset_id in {r[0] for r in media_references(profile.portfolio)}
    if ((upload or remove) and not owner) or (not owner and not public):
        raise HTTPException(404, 'Archivo no disponible.')
    if remove and company and company.foto_id == asset_id:
        raise HTTPException(409, 'Quita la foto del perfil y guarda antes de eliminarla.')
    if upload and asset.creado < datetime.utcnow() - timedelta(minutes=15):
        raise HTTPException(409, 'La reserva expiró. Selecciona nuevamente tu archivo.')
    if remove and profile and asset_id in {r[0] for r in media_references(profile.portfolio or {})}:
        raise HTTPException(409, 'Quita el archivo del portafolio y guarda antes de eliminarlo.')
    if not upload and not remove and not asset.verificado:
        raise HTTPException(404, 'El archivo aún no está verificado.')
    return {'pathname':asset.pathname, 'mime':asset.mime, 'tamano':asset.tamano, 'tipo':asset.tipo}

def media_service(x_media_service: str=Header(default='')):
    secret=os.getenv('MEDIA_SERVICE_SECRET','')
    if not secret or not secrets.compare_digest(secret,x_media_service):
        raise HTTPException(403, 'Operación reservada al servicio de archivos.')

@router.post('/media/{asset_id}/verified', dependencies=[Depends(media_service)])
def verified(asset_id: str, user=Depends(current_user), db: Session=Depends(get_db)):
    asset=db.get(ArchivoPortfolio,asset_id)
    if not asset or asset.usuario_id!=user.id: raise HTTPException(404,'Archivo no encontrado.')
    asset.verificado=True
    db.commit()
    return {'ok':True}

@router.delete('/media/{asset_id}', status_code=204, dependencies=[Depends(media_service)])
def remove_reservation(asset_id: str, user=Depends(current_user), db: Session=Depends(get_db)):
    profile = db.query(PerfilEgresado).filter_by(usuario_id=user.id).first()
    company = db.query(PerfilEmpresa).filter_by(usuario_id=user.id).first()
    asset = db.get(ArchivoPortfolio, asset_id)
    if not asset or asset.usuario_id != user.id: raise HTTPException(404, 'Archivo no encontrado.')
    if (profile and asset_id in {r[0] for r in media_references(profile.portfolio or {})}) or (company and company.foto_id == asset_id):
        raise HTTPException(409, 'Quita el archivo del portafolio y guarda antes de eliminarlo.')
    db.delete(asset)
    db.commit()
