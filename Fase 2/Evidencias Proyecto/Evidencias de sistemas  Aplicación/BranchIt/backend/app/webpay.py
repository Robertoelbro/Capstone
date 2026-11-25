"""Small Webpay Plus REST client. This implementation cannot target production.

Reference: TransbankDevelopers/transbank-developers-docs, referencia/webpay.
Credentials and redirect destinations come exclusively from server settings.
"""
from dataclasses import dataclass, field
import json
import os
import re
from urllib.parse import urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler

from .config import CORS_ORIGINS

PAYMENT_URL = 'https://webpay3gint.transbank.cl/webpayserver/initTransaction'
API_URL = 'https://webpay3gint.transbank.cl/rswebpaytransaction/api/webpay/v1.2/transactions'
TOKEN = re.compile(r'^[a-fA-F0-9]{64}$')


class PaymentProviderError(Exception):
    pass


@dataclass(frozen=True)
class WebpaySettings:
    commerce_code: str = field(repr=False)
    api_key: str = field(repr=False)
    return_url: str
    frontend_url: str
    entorno: str = 'integration'


def settings():
    # Fail closed: even an accidental production credential/environment cannot
    # direct this release at the production API.
    if os.getenv('WEBPAY_ENABLED', '').lower() != 'true' or os.getenv('WEBPAY_ENV', '') != 'integration':
        return None
    code, key = os.getenv('WEBPAY_COMMERCE_CODE', ''), os.getenv('WEBPAY_API_KEY', '')
    callback, frontend = os.getenv('WEBPAY_RETURN_URL', ''), os.getenv('WEBPAY_FRONTEND_URL', '').rstrip('/')
    if not re.fullmatch(r'[0-9]{12}', code) or not re.fullmatch(r'[a-fA-F0-9]{64}', key):
        return None
    try:
        target, front = urlsplit(callback), urlsplit(frontend)
        def safe_origin(parts):
            return (parts.scheme == 'https' or (parts.scheme == 'http' and parts.hostname in ('127.0.0.1', 'localhost'))) and bool(parts.hostname) and not parts.username and not parts.password
        if (not safe_origin(target) or not safe_origin(front) or target.path != '/billing/return'
                or target.query or target.fragment or len(callback) > 256
                or front.path or front.query or front.fragment or frontend not in CORS_ORIGINS):
            return None
        # Validate malformed ports as well, without exposing the configured URL.
        _ = target.port, front.port
    except ValueError:
        return None
    return WebpaySettings(code, key, callback, frontend)


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class WebpayProvider:
    def __init__(self, config):
        self.config = config

    def _request(self, method, token=None, payload=None):
        if token is not None and not TOKEN.fullmatch(token):
            raise PaymentProviderError('Respuesta de pago no válida.')
        endpoint = API_URL + ('/' + token if token is not None else '')
        body = json.dumps(payload).encode() if payload is not None else (b'{}' if method == 'PUT' else None)
        request = Request(endpoint, method=method, data=body, headers={
            'Tbk-Api-Key-Id': self.config.commerce_code,
            'Tbk-Api-Key-Secret': self.config.api_key,
            'Content-Type': 'application/json', 'Accept': 'application/json'})
        try:
            with build_opener(_NoRedirect()).open(request, timeout=10) as response:
                raw = response.read(65537)
                if len(raw) > 65536:
                    raise ValueError
                result = json.loads(raw)
                if not isinstance(result, dict):
                    raise ValueError
                return result
        except Exception:
            # Provider exceptions may contain URLs/tokens/headers. Never echo them.
            raise PaymentProviderError('No fue posible confirmar el estado con Webpay. Revisa la orden antes de reintentar.') from None

    def create(self, order):
        return self._request('POST', payload={'buy_order': order.buy_order, 'session_id': order.session_id,
            'amount': order.monto_clp, 'return_url': self.config.return_url})

    def commit(self, token):
        return self._request('PUT', token=token)

    def status(self, token):
        return self._request('GET', token=token)
