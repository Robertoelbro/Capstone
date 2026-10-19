from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..security import hash_password

router = APIRouter(prefix="/auth", tags=["registro"])


@router.post(
    "/registro/egresado",
    response_model=schemas.UsuarioOut,
    status_code=status.HTTP_201_CREATED,
)
def registrar_egresado(datos: schemas.RegistroEgresado, db: Session = Depends(get_db)):
    existente = db.query(models.Usuario).filter(models.Usuario.email == datos.email).first()
    if existente:
        raise HTTPException(status_code=400, detail="Ese correo ya está registrado")

    usuario = models.Usuario(
        email=datos.email,
        password_hash=hash_password(datos.password),
        tipo=models.TipoUsuario.egresado,
    )
    db.add(usuario)
    db.flush()  # para obtener usuario.id antes del commit

    perfil = models.PerfilEgresado(
        usuario_id=usuario.id,
        nombre=datos.nombre,
        apellido=datos.apellido,
        carrera=datos.carrera,
        anio_egreso=datos.anio_egreso,
    )
    db.add(perfil)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.post(
    "/registro/empresa",
    response_model=schemas.UsuarioOut,
    status_code=status.HTTP_201_CREATED,
)
def registrar_empresa(datos: schemas.RegistroEmpresa, db: Session = Depends(get_db)):
    existente = db.query(models.Usuario).filter(models.Usuario.email == datos.email).first()
    if existente:
        raise HTTPException(status_code=400, detail="Ese correo ya está registrado")

    usuario = models.Usuario(
        email=datos.email,
        password_hash=hash_password(datos.password),
        tipo=models.TipoUsuario.empresa,
    )
    db.add(usuario)
    db.flush()

    perfil = models.PerfilEmpresa(
        usuario_id=usuario.id,
        nombre_empresa=datos.nombre_empresa,
        rubro=datos.rubro,
        descripcion=datos.descripcion,
        sitio_web=datos.sitio_web,
    )
    db.add(perfil)
    db.commit()
    db.refresh(usuario)
    return usuario
