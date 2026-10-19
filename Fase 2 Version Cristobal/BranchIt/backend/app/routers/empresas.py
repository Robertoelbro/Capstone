from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/empresas", tags=["empresas"])

# Misma nota que en egresados.py: usuario_id/empresa_id se reciben directo
# hasta que exista login; luego se reemplaza por el usuario autenticado.


def _obtener_perfil_empresa_o_404(db: Session, usuario_id: int) -> models.PerfilEmpresa:
    perfil = (
        db.query(models.PerfilEmpresa)
        .filter(models.PerfilEmpresa.usuario_id == usuario_id)
        .first()
    )
    if not perfil:
        raise HTTPException(status_code=404, detail="Perfil de empresa no encontrado")
    return perfil


def _obtener_oferta_o_404(db: Session, empresa_id: int, oferta_id: int) -> models.OfertaEmpleo:
    oferta = (
        db.query(models.OfertaEmpleo)
        .filter(
            models.OfertaEmpleo.id == oferta_id,
            models.OfertaEmpleo.empresa_id == empresa_id,
        )
        .first()
    )
    if not oferta:
        raise HTTPException(status_code=404, detail="Oferta no encontrada")
    return oferta


@router.post(
    "/{usuario_id}/ofertas",
    response_model=schemas.OfertaEmpleoOut,
    status_code=status.HTTP_201_CREATED,
)
def crear_oferta(
    usuario_id: int, datos: schemas.OfertaEmpleoCreate, db: Session = Depends(get_db)
):
    perfil_empresa = _obtener_perfil_empresa_o_404(db, usuario_id)
    oferta = models.OfertaEmpleo(empresa_id=perfil_empresa.id, **datos.model_dump())
    db.add(oferta)
    db.commit()
    db.refresh(oferta)
    return oferta


@router.get("/{usuario_id}/ofertas", response_model=list[schemas.OfertaEmpleoOut])
def listar_mis_ofertas(usuario_id: int, db: Session = Depends(get_db)):
    perfil_empresa = _obtener_perfil_empresa_o_404(db, usuario_id)
    return (
        db.query(models.OfertaEmpleo)
        .filter(models.OfertaEmpleo.empresa_id == perfil_empresa.id)
        .order_by(models.OfertaEmpleo.fecha_publicacion.desc())
        .all()
    )


@router.get("/{usuario_id}/ofertas/{oferta_id}", response_model=schemas.OfertaEmpleoOut)
def leer_oferta(usuario_id: int, oferta_id: int, db: Session = Depends(get_db)):
    perfil_empresa = _obtener_perfil_empresa_o_404(db, usuario_id)
    return _obtener_oferta_o_404(db, perfil_empresa.id, oferta_id)


@router.put("/{usuario_id}/ofertas/{oferta_id}", response_model=schemas.OfertaEmpleoOut)
def actualizar_oferta(
    usuario_id: int,
    oferta_id: int,
    datos: schemas.OfertaEmpleoUpdate,
    db: Session = Depends(get_db),
):
    perfil_empresa = _obtener_perfil_empresa_o_404(db, usuario_id)
    oferta = _obtener_oferta_o_404(db, perfil_empresa.id, oferta_id)
    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(oferta, campo, valor)
    db.commit()
    db.refresh(oferta)
    return oferta


@router.delete("/{usuario_id}/ofertas/{oferta_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_oferta(usuario_id: int, oferta_id: int, db: Session = Depends(get_db)):
    perfil_empresa = _obtener_perfil_empresa_o_404(db, usuario_id)
    oferta = _obtener_oferta_o_404(db, perfil_empresa.id, oferta_id)
    db.delete(oferta)
    db.commit()
    return None
