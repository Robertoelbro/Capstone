from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict

from .models import TipoUsuario


# ---------- Registro / Usuario ----------

class RegistroEgresado(BaseModel):
    email: EmailStr
    password: str
    nombre: str
    apellido: str
    carrera: Optional[str] = None
    anio_egreso: Optional[int] = None


class RegistroEmpresa(BaseModel):
    email: EmailStr
    password: str
    nombre_empresa: str
    rubro: Optional[str] = None
    descripcion: Optional[str] = None
    sitio_web: Optional[str] = None


class UsuarioOut(BaseModel):
    id: int
    email: EmailStr
    tipo: TipoUsuario
    fecha_registro: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------- Perfil Egresado ----------

class PerfilEgresadoBase(BaseModel):
    nombre: str
    apellido: str
    carrera: Optional[str] = None
    anio_egreso: Optional[int] = None
    presentacion: Optional[str] = None
    linkedin_url: Optional[str] = None
    foto_url: Optional[str] = None


class PerfilEgresadoUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    carrera: Optional[str] = None
    anio_egreso: Optional[int] = None
    presentacion: Optional[str] = None
    linkedin_url: Optional[str] = None
    foto_url: Optional[str] = None


class PerfilEgresadoOut(PerfilEgresadoBase):
    id: int
    usuario_id: int

    model_config = ConfigDict(from_attributes=True)


# ---------- Perfil Empresa ----------

class PerfilEmpresaOut(BaseModel):
    id: int
    usuario_id: int
    nombre_empresa: str
    rubro: Optional[str] = None
    descripcion: Optional[str] = None
    sitio_web: Optional[str] = None
    logo_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ---------- Oferta de empleo ----------

class OfertaEmpleoBase(BaseModel):
    titulo: str
    descripcion: str
    requisitos: Optional[str] = None
    ubicacion: Optional[str] = None
    modalidad: Optional[str] = None


class OfertaEmpleoCreate(OfertaEmpleoBase):
    pass


class OfertaEmpleoUpdate(BaseModel):
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    requisitos: Optional[str] = None
    ubicacion: Optional[str] = None
    modalidad: Optional[str] = None
    activa: Optional[bool] = None


class OfertaEmpleoOut(OfertaEmpleoBase):
    id: int
    empresa_id: int
    fecha_publicacion: datetime
    activa: bool

    model_config = ConfigDict(from_attributes=True)


class OfertaEmpleoConEmpresa(OfertaEmpleoOut):
    """Version de la oferta que incluye el nombre de la empresa, para el hub del egresado."""

    nombre_empresa: str
