from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix='/api/employment', tags=['ofertas'])


@router.get('/jobs', response_model=list[schemas.OfertaEmpleoConEmpresa])
def list_jobs(db: Session = Depends(get_db)):
    rows = (db.query(models.OfertaEmpleo, models.PerfilEmpresa.nombre_empresa)
            .join(models.PerfilEmpresa).filter(models.OfertaEmpleo.activa.is_(True))
            .order_by(models.OfertaEmpleo.fecha_publicacion.desc()).all())
    return [dict(schemas.OfertaEmpleoOut.model_validate(job).model_dump(), nombre_empresa=company)
            for job, company in rows]


@router.get('/jobs/{job_id}', response_model=schemas.OfertaEmpleoConEmpresa)
def job_detail(job_id: int, db: Session = Depends(get_db)):
    job = db.get(models.OfertaEmpleo, job_id)
    if not job:
        raise HTTPException(404, 'Oferta no encontrada.')
    return dict(schemas.OfertaEmpleoOut.model_validate(job).model_dump(), nombre_empresa=job.empresa.nombre_empresa)
