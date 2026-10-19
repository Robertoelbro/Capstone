from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from .config import SECRET_KEY
from .database import get_db
from .models import Usuario

bearer = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), password_hash.encode())
    except ValueError:
        return False


def create_token(user_id: int, token_version: int = 0) -> str:
    if len(SECRET_KEY) < 32:
        raise HTTPException(503, 'Configura una SECRET_KEY de al menos 32 caracteres en el servidor.')
    now = datetime.now(timezone.utc)
    return jwt.encode({'sub': str(user_id), 'ver': token_version, 'iat': now, 'exp': now + timedelta(hours=2)}, SECRET_KEY, algorithm='HS256')


def current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    denied = HTTPException(401, 'Tu sesión no es válida o ha expirado. Inicia sesión nuevamente.', headers={'WWW-Authenticate': 'Bearer'})
    if not credentials or len(SECRET_KEY) < 32:
        raise denied
    try:
        claims = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=['HS256'], options={'require_exp': True, 'require_sub': True})
        user = db.get(Usuario, int(claims['sub']))
    except (JWTError, ValueError, TypeError):
        raise denied
    if not user or not user.activo or claims.get('ver') != user.token_version:
        raise denied
    return user


def require_owner(role: str):
    def check(usuario_id: int, user: Usuario = Depends(current_user)):
        if user.id != usuario_id or user.tipo.value != role:
            raise HTTPException(403, 'No tienes permiso para acceder a estos datos.')
        return user
    return check
