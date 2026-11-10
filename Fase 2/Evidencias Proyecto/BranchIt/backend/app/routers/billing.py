"""Billing preparation only: no charge, redirect, callback or entitlement activation."""
from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..database import get_db
from ..security import current_user
from ..subscription_models import Subscription, subscription_active

router = APIRouter(prefix='/billing', tags=['suscripción'])
PRICE_CLP = 2990
BENEFITS = ['Prácticas de entrevista sin límite diario de BranchIT', 'Candidato destacado en tus postulaciones']


class SubscriptionOut(BaseModel):
    precio_clp: int = PRICE_CLP
    periodicidad: Literal['mensual'] = 'mensual'
    estado: Literal['inactiva', 'activa']
    vigente_hasta: datetime | None = None
    beneficios: list[str] = Field(default_factory=lambda: list(BENEFITS))
    pago_habilitado: bool = False
    pasarela: Literal['Webpay'] = 'Webpay'
    configuracion_pendiente: bool = True


def graduate(user):
    if user.tipo.value != 'egresado':
        raise HTTPException(403, 'La suscripción está disponible solo para egresados.')


@router.get('/me', response_model=SubscriptionOut)
def subscription_status(user=Depends(current_user), db: Session = Depends(get_db)):
    graduate(user)
    row = db.query(Subscription).filter_by(usuario_id=user.id).first()
    expiration = row.vigente_hasta if row else None
    # SQLite returns naive datetimes; production stores timezone-aware PostgreSQL values.
    if expiration and expiration.tzinfo is None:
        expiration = expiration.replace(tzinfo=timezone.utc)
    active = subscription_active(row)
    return SubscriptionOut(estado='activa' if active else 'inactiva', vigente_hasta=expiration)


@router.post('/checkout', status_code=503)
def checkout(user=Depends(current_user)):
    graduate(user)
    # Deliberately fail closed even if environment variables or query flags are set.
    # Payment creation/confirmation and entitlements require a separately reviewed implementation.
    raise HTTPException(503, 'Los pagos con Webpay todavía no están habilitados. No se ha realizado ningún cobro.')
