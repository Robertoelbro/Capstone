from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from pydantic import Field, field_validator

from .. import models, schemas
from ..database import get_db
from ..rate_limit import limit_auth
from ..security import hash_password, verify_password, create_token, current_user
from .notifications import notify_job_change

router = APIRouter(prefix="/auth", tags=["cuentas"])
DUMMY_HASH = hash_password("branchit-invalid-login")


def register(data, role, db):
    email = data.email.lower()
    if db.query(models.Usuario).filter(func.lower(models.Usuario.email) == email).first():
        raise HTTPException(409, "Ese correo ya está registrado.")
    if db.query(models.Usuario).filter_by(rut=data.rut).first():
        raise HTTPException(409, "Ese RUT ya está registrado.")
    user = models.Usuario(email=email, password_hash=hash_password(data.password), tipo=role,
                          rut=data.rut, telefono=data.telefono, fecha_identidad=data.fecha_identidad)
    db.add(user)
    try:
        db.flush()
        values = data.model_dump(exclude={"email", "password", "rut", "telefono", "fecha_identidad"})
        profile = models.PerfilEgresado if role == models.TipoUsuario.egresado else models.PerfilEmpresa
        db.add(profile(usuario_id=user.id, **values))
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "No se pudo crear la cuenta. Verifica si el correo ya está registrado.")
    db.refresh(user)
    return user


@router.post("/registro/egresado", response_model=schemas.UsuarioOut, status_code=201, dependencies=[Depends(limit_auth)])
def register_graduate(data: schemas.RegistroEgresado, db: Session = Depends(get_db)):
    return register(data, models.TipoUsuario.egresado, db)


@router.post("/registro/empresa", response_model=schemas.UsuarioOut, status_code=201, dependencies=[Depends(limit_auth)])
def register_company(data: schemas.RegistroEmpresa, db: Session = Depends(get_db)):
    return register(data, models.TipoUsuario.empresa, db)


@router.post("/login", response_model=schemas.SessionOut, dependencies=[Depends(limit_auth)])
def login(data: schemas.Login, db: Session = Depends(get_db)):
    user = db.query(models.Usuario).filter(func.lower(models.Usuario.email) == data.email.lower()).first()
    valid = verify_password(data.password, user.password_hash if user else DUMMY_HASH)
    if not user or not valid or not user.activo:
        raise HTTPException(401, "Correo o contraseña incorrectos.")
    return {"access_token": create_token(user.id, user.token_version), "user": user}


@router.get("/me", response_model=schemas.UsuarioOut)
def me(user=Depends(current_user)):
    return user


@router.post('/logout', status_code=204)
def logout(user=Depends(current_user), db: Session = Depends(get_db)):
    db.execute(update(models.Usuario).where(models.Usuario.id == user.id).values(token_version=models.Usuario.token_version + 1))
    db.commit()


@router.post('/password', response_model=schemas.SessionOut, dependencies=[Depends(limit_auth)])
def change_password(data: schemas.CambioPassword, user=Depends(current_user), db: Session=Depends(get_db)):
    # Serialize concurrent password changes and invalidate every previous JWT.
    user = db.query(models.Usuario).filter_by(id=user.id).populate_existing().with_for_update().one()
    if not verify_password(data.password_actual, user.password_hash):
        raise HTTPException(400, 'La contraseña actual no es correcta.')
    if data.password_actual == data.password:
        raise HTTPException(422, 'Elige una contraseña distinta de la actual.')
    user.password_hash = hash_password(data.password)
    user.token_version += 1
    db.commit()
    return {'access_token': create_token(user.id, user.token_version), 'user': user}


class DesactivarCuenta(schemas.InputModel):
    password_actual: str = Field(min_length=1, max_length=72)

    @field_validator('password_actual')
    @classmethod
    def password_bytes(cls, value):
        if len(value.encode('utf-8')) > 72:
            raise ValueError('La contraseña no debe superar 72 bytes UTF-8.')
        return value


@router.post('/deactivate', status_code=204, dependencies=[Depends(limit_auth)])
def deactivate(data: DesactivarCuenta, user=Depends(current_user), db: Session = Depends(get_db)):
    user = db.query(models.Usuario).filter_by(id=user.id).populate_existing().with_for_update().one()
    if not verify_password(data.password_actual, user.password_hash):
        raise HTTPException(400, 'La contraseña actual no es correcta.')
    if user.tipo == models.TipoUsuario.empresa and user.perfil_empresa:
        jobs = db.query(models.OfertaEmpleo).filter_by(
            empresa_id=user.perfil_empresa.id, activa=True).with_for_update().all()
        for job in jobs:
            job.activa = False
            notify_job_change(db, job, False)
    user.activo = False
    user.token_version += 1
    db.commit()
