from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import auth, egresados, empresas

app = FastAPI(
    title="BranchIT API",
    version="0.1.0",
)

# Permite que el frontend (Vite, localhost:5173) llame a la API en desarrollo.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(egresados.router)
app.include_router(empresas.router)


@app.get("/")
def root():
    return {"message": "BranchIT API funcionando"}
