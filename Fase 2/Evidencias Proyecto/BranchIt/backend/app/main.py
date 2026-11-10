from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from sqlalchemy.orm import Session
from fastapi import Depends
from .database import get_db
from .request_guard import RequestGuard, SECURITY_HEADERS
from .config import CORS_ORIGINS
from .routers import auth, egresados, empresas, jobs, applications
from .routers import portfolio, assistant, notifications, career, billing

app = FastAPI(
    title="BranchIT API",
    version="0.1.0"
)

app.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS,
                   allow_methods=['GET', 'POST', 'PUT', 'DELETE'], allow_headers=['Content-Type', 'Authorization'])
app.add_middleware(RequestGuard)
app.include_router(auth.router)
app.include_router(egresados.router)
app.include_router(empresas.router)
app.include_router(jobs.router)
app.include_router(applications.router)
app.include_router(portfolio.router)
app.include_router(assistant.router)
app.include_router(notifications.router)
app.include_router(career.router)
app.include_router(billing.router)


@app.exception_handler(RequestValidationError)
async def validation_error(request, exc):
    # Do not echo password/contact/answer inputs in validation responses.
    errors = [{'loc': item['loc'], 'msg': item['msg'], 'type': item['type']} for item in exc.errors()]
    return JSONResponse(status_code=422, content={'detail': errors})


@app.exception_handler(SQLAlchemyError)
async def database_unavailable(request, exc):
    return JSONResponse(status_code=503, content={
        'detail': 'El servicio de datos no está disponible. Inténtalo nuevamente en unos momentos.'
    })


@app.exception_handler(Exception)
async def unexpected_error(request, exc):
    # Never disclose SQL parameters, tokens or provider errors to the browser.
    return JSONResponse(status_code=500, headers=SECURITY_HEADERS, content={
        'detail': 'No pudimos completar la operación. Inténtalo nuevamente.'
    })


@app.get('/health')
def health():
    return {'estado': 'ok'}


@app.get('/health/ready')
def readiness(db: Session = Depends(get_db)):
    # Checks required schema, without exposing data or credentials.
    for statement in ('SELECT usuario_id, limite_experiencia FROM seguimiento_laboral LIMIT 1',
                      'SELECT usuario_id, estado, vigente_hasta FROM suscripciones LIMIT 1',
                      'SELECT creada FROM entrevistas_ia LIMIT 1'):
        db.execute(text(statement)).first()
    return {'estado': 'listo'}

@app.get("/")
def root():
    return {"message": "BranchIT API funcionando"}
