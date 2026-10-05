from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..security import require_owner

router = APIRouter(prefix="/egresados", tags=["egresados"], dependencies=[Depends(require_owner("egresado"))])


def _obtener_perfil_o_404(db: Session, usuario_id: int) -> models.PerfilEgresado:
    perfil = (
        db.query(models.PerfilEgresado)
        .filter(models.PerfilEgresado.usuario_id == usuario_id)
        .first()
    )
    if not perfil:
        raise HTTPException(status_code=404, detail="Perfil de egresado no encontrado")
    return perfil


@router.get("/{usuario_id}", response_model=schemas.PerfilEgresadoOut)
def leer_perfil(usuario_id: int, db: Session = Depends(get_db)):
    return _obtener_perfil_o_404(db, usuario_id)


@router.put("/{usuario_id}", response_model=schemas.PerfilEgresadoOut)
def actualizar_perfil(
    usuario_id: int,
    datos: schemas.PerfilEgresadoUpdate,
    db: Session = Depends(get_db),
):
    perfil = _obtener_perfil_o_404(db, usuario_id)
    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(perfil, campo, valor)
    db.commit()
    db.refresh(perfil)
    return perfil


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_cuenta_egresado(usuario_id: int, db: Session = Depends(get_db)):
    """Elimina la cuenta del egresado completa (usuario + perfil, por cascade)."""
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario or usuario.tipo != models.TipoUsuario.egresado:
        raise HTTPException(status_code=404, detail="Usuario egresado no encontrado")
    db.delete(usuario)
    db.commit()
    return None


@router.get("/{usuario_id}/ofertas", response_model=list[schemas.OfertaEmpleoConEmpresa])
def ver_ofertas_disponibles(usuario_id: int, db: Session = Depends(get_db)):
    """Hub del egresado: lista las ofertas de empleo activas de todas las empresas."""
    _obtener_perfil_o_404(db, usuario_id)  # valida que el egresado exista

    ofertas = (
        db.query(models.OfertaEmpleo, models.PerfilEmpresa.nombre_empresa)
        .join(models.PerfilEmpresa, models.OfertaEmpleo.empresa_id == models.PerfilEmpresa.id)
        .filter(models.OfertaEmpleo.activa.is_(True))
        .order_by(models.OfertaEmpleo.fecha_publicacion.desc())
        .all()
    )

    resultado = []
    for oferta, nombre_empresa in ofertas:
        item = schemas.OfertaEmpleoConEmpresa(**schemas.OfertaEmpleoOut.model_validate(oferta).model_dump(), nombre_empresa=nombre_empresa)
        resultado.append(item)
    return resultado


@router.post('/{usuario_id}/presentacion', response_model=schemas.PerfilEgresadoOut, status_code=201)
def create_presentation(usuario_id: int, data: schemas.PresentacionInput, db: Session = Depends(get_db)):
    profile = _obtener_perfil_o_404(db, usuario_id)
    if profile.presentacion:
        raise HTTPException(409, 'Ya tienes una presentación. Puedes editarla.')
    profile.presentacion = data.presentacion
    db.commit()
    db.refresh(profile)
    return profile


@router.delete('/{usuario_id}/presentacion', status_code=204)
def delete_presentation(usuario_id: int, db: Session = Depends(get_db)):
    profile = _obtener_perfil_o_404(db, usuario_id)
    profile.presentacion = None
    db.commit()
