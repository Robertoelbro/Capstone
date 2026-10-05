from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import OperationalError
from .config import CORS_ORIGINS
from .routers import auth, egresados, empresas, jobs, applications

app = FastAPI(
    title="BranchIT API",
    version="0.1.0"
)

app.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS,
                   allow_methods=['GET', 'POST', 'PUT', 'DELETE'], allow_headers=['Content-Type', 'Authorization'])
app.include_router(auth.router)
app.include_router(egresados.router)
app.include_router(empresas.router)
app.include_router(jobs.router)
app.include_router(applications.router)


@app.middleware('http')
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'no-referrer'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Cache-Control'] = 'no-store'
    return response


@app.exception_handler(RequestValidationError)
async def validation_error(request, exc):
    # Do not echo password/contact/answer inputs in validation responses.
    errors = [{'loc': item['loc'], 'msg': item['msg'], 'type': item['type']} for item in exc.errors()]
    return JSONResponse(status_code=422, content={'detail': errors})


@app.exception_handler(OperationalError)
async def database_unavailable(request, exc):
    return JSONResponse(status_code=503, content={
        'detail': 'El servicio de datos no está disponible. Inténtalo nuevamente en unos momentos.'
    })

@app.get("/")
def root():
    return {"message": "BranchIT API funcionando"}
