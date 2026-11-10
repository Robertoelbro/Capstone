"""Subscription entitlement state; only a verified server-side process may write it."""
from datetime import datetime, timezone
from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, String

from .database import Base


class Subscription(Base):
    __tablename__ = 'suscripciones'
    __table_args__ = (CheckConstraint("estado IN ('inactiva', 'activa')", name='ck_suscripcion_estado'),)

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id', ondelete='CASCADE'), unique=True, nullable=False)
    estado = Column(String(12), nullable=False, default='inactiva')
    vigente_hasta = Column(DateTime(timezone=True), nullable=True)


def subscription_active(row):
    if not row or row.estado != 'activa' or row.vigente_hasta is None:
        return False
    expiration = row.vigente_hasta
    if expiration.tzinfo is None:
        expiration = expiration.replace(tzinfo=timezone.utc)
    return expiration > datetime.now(timezone.utc)


def has_subscription(db, usuario_id):
    return subscription_active(db.query(Subscription).filter_by(usuario_id=usuario_id).first())
