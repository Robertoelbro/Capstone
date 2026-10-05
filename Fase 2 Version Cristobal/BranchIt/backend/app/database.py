import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# En desarrollo local, si no hay variable de entorno, usa Postgres local por defecto.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://branchit:branchit@localhost:5432/branchit",
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependencia de FastAPI: entrega una sesion de BD y la cierra al terminar."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
