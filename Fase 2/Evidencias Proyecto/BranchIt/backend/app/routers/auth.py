from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..rate_limit import limit_auth
from ..security import hash_password, verify_password, create_token, current_user

router = APIRouter(prefix="/auth", tags=["cuentas"])
DUMMY_HASH = hash_password("branchit-invalid-login")


def register(data, role, db):
    email = data.email.lower()
    if db.query(models.Usuario).filter(func.lower(models.Usuario.email) == email).first():
        raise HTTPException(409, "Ese correo ya está registrado.")
    user = models.Usuario(email=email, password_hash=hash_password(data.password), tipo=role)
    db.add(user)
    try:
        db.flush()
        values = data.model_dump(exclude={"email", "password"})
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
