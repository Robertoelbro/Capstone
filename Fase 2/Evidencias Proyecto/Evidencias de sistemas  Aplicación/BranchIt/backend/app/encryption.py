"""Authenticated encryption of application contact information and answers."""
import json
from cryptography.fernet import Fernet, InvalidToken
from fastapi import HTTPException
from .config import DATA_ENCRYPTION_KEY


def cipher():
    try:
        return Fernet(DATA_ENCRYPTION_KEY.encode('ascii'))
    except (ValueError, UnicodeError):
        raise HTTPException(503, 'El servicio de postulaciones no está configurado. Contacta al administrador.')


def encrypt_data(data: dict) -> str:
    return cipher().encrypt(json.dumps(data, ensure_ascii=False).encode('utf-8')).decode('ascii')


def decrypt_data(value: str) -> dict:
    try:
        return json.loads(cipher().decrypt(value.encode('ascii')))
    except (InvalidToken, ValueError, UnicodeError):
        raise HTTPException(503, 'No fue posible recuperar la postulación de forma segura.')
