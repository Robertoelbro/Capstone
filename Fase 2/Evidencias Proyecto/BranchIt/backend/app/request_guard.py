"""Bound JSON requests before parsing; binary uploads go directly to Blob."""
from fastapi.responses import JSONResponse

MAX_REQUEST_BYTES = 512 * 1024
SECURITY_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'Referrer-Policy': 'no-referrer',
    'X-Frame-Options': 'DENY',
    'Cache-Control': 'no-store',
}


class RequestGuard:
    def __init__(self, app, max_bytes=MAX_REQUEST_BYTES):
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http':
            return await self.app(scope, receive, send)

        async def secured_send(message):
            if message['type'] == 'http.response.start':
                headers = list(message.get('headers', []))
                keys = {name.lower().encode() for name in SECURITY_HEADERS}
                headers = [(name, value) for name, value in headers if name.lower() not in keys]
                headers.extend((name.lower().encode(), value.encode()) for name, value in SECURITY_HEADERS.items())
                message = {**message, 'headers': headers}
            await send(message)

        async def reject(code, detail):
            await JSONResponse(status_code=code, content={'detail': detail})(scope, receive, secured_send)

        if scope['method'] not in ('POST', 'PUT', 'PATCH', 'DELETE'):
            return await self.app(scope, receive, secured_send)
        lengths = [value for name, value in scope['headers'] if name.lower() == b'content-length']
        if lengths:
            if len(lengths) != 1 or len(lengths[0]) > 20 or not lengths[0].isdigit():
                return await reject(400, 'El tamaño declarado de la solicitud no es válido.')
            if int(lengths[0]) > self.max_bytes:
                return await reject(413, 'La solicitud supera el límite de 512 KB.')

        chunks, size = [], 0
        while True:
            message = await receive()
            if message['type'] == 'http.disconnect':
                return
            chunk = message.get('body', b'')
            size += len(chunk)
            if size > self.max_bytes:
                return await reject(413, 'La solicitud supera el límite de 512 KB.')
            chunks.append(chunk)
            if not message.get('more_body', False):
                break
        buffered = b''.join(chunks)
        delivered = False

        async def buffered_receive():
            nonlocal delivered
            if not delivered:
                delivered = True
                return {'type': 'http.request', 'body': buffered, 'more_body': False}
            return await receive()

        await self.app(scope, buffered_receive, secured_send)
