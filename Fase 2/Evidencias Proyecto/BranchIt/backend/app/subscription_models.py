"""Subscription entitlement state; only a verified server-side process may write it."""
from datetime import datetime, timezone
from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint

from .database import Base


class Subscription(Base):
    __tablename__ = 'suscripciones'
    __table_args__ = (CheckConstraint("estado IN ('inactiva', 'activa')", name='ck_suscripcion_estado'),)

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id', ondelete='CASCADE'), unique=True, nullable=False)
    estado = Column(String(12), nullable=False, default='inactiva')
    vigente_hasta = Column(DateTime(timezone=True), nullable=True)


class WebpayOrder(Base):
    __tablename__ = 'pagos_webpay'
    __table_args__ = (
        UniqueConstraint('usuario_id', 'request_id', name='uq_pago_solicitud_usuario'),
        CheckConstraint('monto_clp = 2990', name='ck_pago_monto'),
        CheckConstraint("entorno = 'integration'", name='ck_pago_integracion'),
    )
    id = Column(String(36), primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False, index=True)
    request_id = Column(String(36), nullable=False)
    buy_order = Column(String(26), unique=True, nullable=False)
    session_id = Column(String(61), nullable=False)
    monto_clp = Column(Integer, nullable=False)
    entorno = Column(String(16), nullable=False)
    estado = Column(String(16), nullable=False)
    token_digest = Column(String(64), unique=True, nullable=True)
    datos_cifrados = Column(Text, nullable=True)
    creada = Column(DateTime(timezone=True), nullable=False)
    actualizada = Column(DateTime(timezone=True), nullable=False)
    confirmada = Column(DateTime(timezone=True), nullable=True)
    vigente_hasta = Column(DateTime(timezone=True), nullable=True)
    beneficio_aplicado = Column(Boolean, nullable=False, default=False)


def subscription_active(row):
    if not row or row.estado != 'activa' or row.vigente_hasta is None:
        return False
    expiration = row.vigente_hasta
    if expiration.tzinfo is None:
        expiration = expiration.replace(tzinfo=timezone.utc)
    return expiration > datetime.now(timezone.utc)


def has_subscription(db, usuario_id):
    return subscription_active(db.query(Subscription).filter_by(usuario_id=usuario_id).first())
