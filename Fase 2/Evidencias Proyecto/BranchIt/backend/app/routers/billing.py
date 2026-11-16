"""Webpay Plus integration only: durable orders and server-verified entitlements."""
import calendar
import hashlib
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from typing import Literal
from urllib.parse import parse_qs
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from ..database import get_db
from ..encryption import cipher, decrypt_data, encrypt_data
from ..models import Usuario
from ..security import current_user
from ..subscription_models import Subscription, WebpayOrder, subscription_active
from ..webpay import PAYMENT_URL, TOKEN, PaymentProviderError, WebpayProvider, settings

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
    entorno: Literal['integration'] = 'integration'
    modo_prueba: bool = True
    renovacion_automatica: bool = False


class CheckoutInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    request_id: UUID


def graduate(user):
    if user.tipo.value != 'egresado':
        raise HTTPException(403, 'La suscripción está disponible solo para egresados.')


def graduate_user(user=Depends(current_user)):
    graduate(user)
    return user


def enabled_config():
    config = settings()
    if not config:
        raise HTTPException(503, 'Webpay de integración no está configurado. No se ha realizado ningún cobro.')
    return config


def provider_for(config):
    return WebpayProvider(config)


def now():
    return datetime.now(timezone.utc)


def aware(value):
    return value.replace(tzinfo=timezone.utc) if value and value.tzinfo is None else value


def calendar_month(value):
    year, month = value.year + (value.month == 12), value.month % 12 + 1
    return value.replace(year=year, month=month, day=min(value.day, calendar.monthrange(year, month)[1]))


def stale_payment(row):
    # Transbank documents a five-minute payment-form window. Once it has passed,
    # do not hand the old token back to the browser or infer a financial result.
    return aware(row.creada) < now() - timedelta(minutes=5)


def effective_status(row):
    if row.estado == 'creando' and aware(row.creada) < now() - timedelta(minutes=2):
        return 'incierta'
    if row.estado == 'pendiente' and stale_payment(row):
        return 'incierta'
    return row.estado


def order_data(row):
    return {'order_id': row.id, 'estado': effective_status(row), 'precio_clp': row.monto_clp,
            'creada': row.creada, 'confirmada': row.confirmada, 'vigente_hasta': row.vigente_hasta,
            'beneficio_aplicado': row.beneficio_aplicado, 'entorno': row.entorno, 'modo_prueba': True,
            'puede_reconciliar': bool(row.token_digest) and not row.beneficio_aplicado}


def checkout_data(row):
    data = decrypt_data(row.datos_cifrados) if row.datos_cifrados else {}
    available = effective_status(row) == 'pendiente' and not row.beneficio_aplicado
    return {'order_id': row.id, 'estado': effective_status(row), 'entorno': row.entorno,
            'url': PAYMENT_URL if available else None, 'token': data.get('token') if available else None}


@router.get('/me', response_model=SubscriptionOut)
def subscription_status(user=Depends(graduate_user), db: Session = Depends(get_db)):
    row = db.query(Subscription).filter_by(usuario_id=user.id).first()
    config = settings()
    return SubscriptionOut(estado='activa' if subscription_active(row) else 'inactiva',
        vigente_hasta=aware(row.vigente_hasta) if row else None,
        pago_habilitado=config is not None, configuracion_pendiente=config is None)


@router.post('/checkout')
def checkout(data: CheckoutInput, user=Depends(graduate_user), config=Depends(enabled_config), db: Session = Depends(get_db)):
    cipher()  # Validate private encryption setup before creating a provider order.
    db.query(Usuario).filter_by(id=user.id).populate_existing().with_for_update().one()
    if not user.activo:
        raise HTTPException(401, 'La cuenta está desactivada.')
    existing = db.query(WebpayOrder).filter_by(usuario_id=user.id, request_id=str(data.request_id)).first()
    if existing:
        if existing.estado == 'creando' and aware(existing.creada) < now() - timedelta(minutes=2):
            existing.estado, existing.actualizada = 'incierta', now()
            db.commit()
        return checkout_data(existing)
    uid = uuid4()
    order = WebpayOrder(id=str(uid), usuario_id=user.id, request_id=str(data.request_id),
        buy_order='BI' + uid.hex[:24], session_id=uuid4().hex, monto_clp=PRICE_CLP,
        entorno='integration', estado='creando', creada=now(), actualizada=now(), beneficio_aplicado=False)
    db.add(order)
    # Persist intent BEFORE a network call. A timeout never repeats create for the
    # same request_id, even if Transbank already accepted that first request.
    db.commit()
    try:
        result = provider_for(config).create(order)
        token = result.get('token')
        if not isinstance(token, str) or not TOKEN.fullmatch(token) or result.get('url') != PAYMENT_URL:
            raise PaymentProviderError()
        encrypted = encrypt_data({'token': token})
        digest = hashlib.sha256(token.encode('ascii')).hexdigest()
    except PaymentProviderError:
        order = _locked_order(db, order.id)
        order.estado, order.actualizada = 'incierta', now()
        db.commit()
        return checkout_data(order)
    order = _locked_order(db, order.id)
    order.token_digest, order.datos_cifrados = digest, encrypted
    order.estado, order.actualizada = 'pendiente', now()
    db.commit()
    return checkout_data(order)


def _locked_order(db, order_id):
    row = db.get(WebpayOrder, order_id)
    if not row:
        raise HTTPException(404, 'Orden no encontrada.')
    # Same account -> order lock order on callback, checkout retries and reconcile.
    db.query(Usuario).filter_by(id=row.usuario_id).with_for_update().one()
    return db.query(WebpayOrder).filter_by(id=order_id).populate_existing().with_for_update().one()


def _verified_result(result, order):
    try:
        if (result.get('buy_order') != order.buy_order or result.get('session_id') != order.session_id
                or isinstance(result.get('amount'), bool)
                or not Decimal(str(result.get('amount'))).is_finite()
                or Decimal(str(result.get('amount'))) != order.monto_clp):
            raise PaymentProviderError()
    except (InvalidOperation, ValueError, TypeError):
        raise PaymentProviderError() from None
    return result.get('status')


def _settle(db, row, config, *, allow_commit=False, cancelled=False, expired=False):
    if row.beneficio_aplicado:
        return row
    if not row.datos_cifrados or row.entorno != 'integration':
        return row
    token = decrypt_data(row.datos_cifrados).get('token', '')
    if not isinstance(token, str) or not TOKEN.fullmatch(token) or hashlib.sha256(token.encode()).hexdigest() != row.token_digest:
        raise HTTPException(503, 'No fue posible recuperar la referencia privada del pago.')
    provider = provider_for(config)
    try:
        result = provider.status(token)
        status = _verified_result(result, row)
        if status == 'INITIALIZED' and allow_commit and not cancelled:
            try:
                result = provider.commit(token)
            except PaymentProviderError:
                # A commit can succeed at Transbank while its response is lost.
                # Query status rather than blindly repeating it or granting access.
                result = provider.status(token)
            status = _verified_result(result, row)
        if status == 'AUTHORIZED' and type(result.get('response_code')) is int and result['response_code'] == 0:
            subscription = db.query(Subscription).filter_by(usuario_id=row.usuario_id).first()
            if not subscription:
                subscription = Subscription(usuario_id=row.usuario_id, estado='inactiva')
                db.add(subscription)
            start = max(now(), aware(subscription.vigente_hasta)) if subscription_active(subscription) else now()
            expiration = calendar_month(start)
            subscription.estado, subscription.vigente_hasta = 'activa', expiration
            row.estado, row.beneficio_aplicado = 'autorizada', True
            row.confirmada, row.vigente_hasta = now(), expiration
        elif status in ('FAILED', 'REVERSED', 'NULLIFIED', 'PARTIALLY_NULLIFIED', 'CAPTURED'):
            row.estado = 'rechazada'
        elif status == 'INITIALIZED':
            row.estado = 'incierta' if stale_payment(row) else 'cancelada' if cancelled else 'expirada' if expired else 'pendiente'
        else:
            row.estado = 'incierta'
    except PaymentProviderError:
        row.estado = 'incierta'
    row.actualizada = now()
    # State and entitlement are committed atomically; row.beneficio_aplicado
    # prevents a replay, concurrent callback or lost response extending twice.
    db.commit()
    return row


def _own_order(db, order_id, user):
    row = db.query(WebpayOrder).filter_by(id=str(order_id), usuario_id=user.id).first()
    if not row:
        raise HTTPException(404, 'Orden no encontrada.')
    return row


@router.get('/orders/{order_id}')
def payment_order(order_id: UUID, user=Depends(graduate_user), db: Session = Depends(get_db)):
    return order_data(_own_order(db, order_id, user))


@router.post('/orders/{order_id}/reconcile')
def reconcile(order_id: UUID, user=Depends(graduate_user), config=Depends(enabled_config), db: Session = Depends(get_db)):
    row = _own_order(db, order_id, user)
    return order_data(_settle(db, _locked_order(db, row.id), config))


def _return_payment(params, db):
    normal, aborted = params.get('token_ws'), params.get('TBK_TOKEN')
    token = normal or aborted
    if token:
        if not TOKEN.fullmatch(token) or (normal and aborted and normal != aborted):
            raise HTTPException(404, 'Orden no encontrada.')
        row = db.query(WebpayOrder).filter_by(token_digest=hashlib.sha256(token.encode()).hexdigest()).first()
    else:
        row = db.query(WebpayOrder).filter_by(buy_order=params.get('TBK_ORDEN_COMPRA', ''),
            session_id=params.get('TBK_ID_SESION') or params.get('TBK_ID_SESSION', '')).first()
    if not row:
        raise HTTPException(404, 'Orden no encontrada.')
    if ((params.get('TBK_ORDEN_COMPRA') and params['TBK_ORDEN_COMPRA'] != row.buy_order)
            or ((params.get('TBK_ID_SESION') or params.get('TBK_ID_SESSION'))
                and (params.get('TBK_ID_SESION') or params.get('TBK_ID_SESSION')) != row.session_id)):
        raise HTTPException(400, 'El retorno de pago no coincide con la orden.')
    config = enabled_config()
    row = _settle(db, _locked_order(db, row.id), config, allow_commit=bool(normal and not aborted),
        cancelled=bool(aborted), expired=not bool(token))
    return RedirectResponse(f'{config.frontend_url}/suscripcion?orden={row.id}', status_code=303)


@router.get('/return')
@router.post('/return')
async def payment_return(request: Request, db: Session = Depends(get_db)):
    raw = request.url.query
    if request.method == 'POST':
        if request.headers.get('content-type', '').split(';')[0].strip() != 'application/x-www-form-urlencoded':
            raise HTTPException(415, 'El formato del retorno no es válido.')
        body = await request.body()
        if len(body) > 4096:
            raise HTTPException(400, 'El retorno de pago no es válido.')
        try:
            raw += ('&' if raw else '') + body.decode('ascii')
        except UnicodeError:
            raise HTTPException(400, 'El retorno de pago no es válido.')
    if len(raw) > 8192:
        raise HTTPException(400, 'El retorno de pago no es válido.')
    try:
        fields = parse_qs(raw, keep_blank_values=True, max_num_fields=10)
        if any(len(values) != 1 for values in fields.values()):
            raise ValueError
        params = {key: values[0] for key, values in fields.items()}
    except ValueError:
        raise HTTPException(400, 'El retorno de pago no es válido.')
    return await run_in_threadpool(_return_payment, params, db)
