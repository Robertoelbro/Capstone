from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator, model_validator
from typing import Annotated, Literal
from urllib.parse import urlsplit

Name = Annotated[str, Field(min_length=1, max_length=100)]


class InputModel(BaseModel):
    model_config = ConfigDict(extra="forbid")
    @field_validator("*", mode="before")
    @classmethod
    def trim_strings(cls, value, info):
        return value.strip() if isinstance(value, str) and info.field_name != "password" else value

    @field_validator("email", mode="after", check_fields=False)
    @classmethod
    def normalize_email(cls, value):
        return value.lower()

    @field_validator("password", check_fields=False)
    @classmethod
    def password_bytes(cls, value):
        if len(value.encode("utf-8")) > 72:
            raise ValueError("La contraseña no debe superar 72 bytes UTF-8.")
        return value

    @field_validator('linkedin_url', 'foto_url', 'sitio_web', 'cv_url', check_fields=False)
    @classmethod
    def safe_url(cls, value):
        if value:
            parsed = urlsplit(value)
            if parsed.scheme not in ('http', 'https') or not parsed.netloc or parsed.username or parsed.password:
                raise ValueError('Utiliza una URL http o https válida y sin credenciales.')
        return value

    @model_validator(mode="after")
    def non_null_required_fields(self):
        for name in ("nombre", "apellido", "titulo", "descripcion", "activa"):
            if name in self.model_fields_set and getattr(self, name) is None and type(self).__name__ in ("PerfilEgresadoUpdate", "OfertaEmpleoUpdate"):
                raise ValueError(f"El campo {name} no puede ser nulo.")
        return self

from .models import TipoUsuario


# ---------- Registro / Usuario ----------

class RegistroEgresado(InputModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    nombre: Name
    apellido: Name
    carrera: Optional[Annotated[str, Field(max_length=150)]] = None
    anio_egreso: Optional[int] = None


class RegistroEmpresa(InputModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    nombre_empresa: Annotated[str, Field(min_length=1, max_length=150)]
    rubro: Optional[Annotated[str, Field(max_length=150)]] = None
    descripcion: Optional[str] = None
    sitio_web: Optional[Annotated[str, Field(max_length=255)]] = None


class UsuarioOut(BaseModel):
    id: int
    email: EmailStr
    tipo: TipoUsuario
    fecha_registro: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------- Perfil Egresado ----------

class PerfilEgresadoBase(InputModel):
    nombre: Name
    apellido: Name
    carrera: Optional[Annotated[str, Field(max_length=150)]] = None
    anio_egreso: Optional[int] = None
    presentacion: Optional[Annotated[str, Field(max_length=5000)]] = None
    linkedin_url: Optional[Annotated[str, Field(max_length=255)]] = None
    foto_url: Optional[Annotated[str, Field(max_length=255)]] = None


class PerfilEgresadoUpdate(InputModel):
    nombre: Optional[Name] = None
    apellido: Optional[Name] = None
    carrera: Optional[Annotated[str, Field(max_length=150)]] = None
    anio_egreso: Optional[int] = None
    presentacion: Optional[Annotated[str, Field(max_length=5000)]] = None
    linkedin_url: Optional[Annotated[str, Field(max_length=255)]] = None
    foto_url: Optional[Annotated[str, Field(max_length=255)]] = None


class PerfilEgresadoOut(PerfilEgresadoBase):
    id: int
    usuario_id: int

    model_config = ConfigDict(from_attributes=True)


# ---------- Perfil Empresa ----------

class PerfilEmpresaOut(BaseModel):
    id: int
    usuario_id: int
    nombre_empresa: Annotated[str, Field(min_length=1, max_length=150)]
    rubro: Optional[Annotated[str, Field(max_length=150)]] = None
    descripcion: Optional[str] = None
    sitio_web: Optional[Annotated[str, Field(max_length=255)]] = None
    logo_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ---------- Oferta de empleo ----------

class Pregunta(InputModel):
    id: str = Field(pattern=r'^[a-zA-Z0-9_-]{1,40}$')
    etiqueta: str = Field(min_length=1, max_length=160)
    tipo: Literal['texto', 'parrafo', 'numero', 'seleccion'] = 'texto'
    obligatoria: bool = True
    opciones: list[Annotated[str, Field(min_length=1, max_length=100)]] = Field(default_factory=list, max_length=15)

    @model_validator(mode='after')
    def valid_options(self):
        if self.tipo == 'seleccion' and (len(self.opciones) < 2 or len(set(self.opciones)) != len(self.opciones)):
            raise ValueError('Una selección necesita al menos dos opciones distintas.')
        if self.tipo != 'seleccion' and self.opciones:
            raise ValueError('Solo las preguntas de selección admiten opciones.')
        return self


class PreguntasModel(InputModel):
    @field_validator('preguntas', check_fields=False)
    @classmethod
    def unique_questions(cls, values):
        if values is None:
            raise ValueError('Las preguntas no pueden ser nulas.')
        if len({p.id for p in values}) != len(values):
            raise ValueError('Las preguntas deben tener identificadores únicos.')
        return values


class OfertaEmpleoBase(PreguntasModel):
    preguntas: list[Pregunta] = Field(default_factory=list, max_length=10)
    titulo: Annotated[str, Field(min_length=1, max_length=150)]
    descripcion: Annotated[str, Field(min_length=1, max_length=10000)]
    requisitos: Optional[str] = None
    ubicacion: Optional[Annotated[str, Field(max_length=150)]] = None
    modalidad: Optional[Annotated[str, Field(max_length=50)]] = None


class OfertaEmpleoCreate(OfertaEmpleoBase):
    pass


class OfertaEmpleoUpdate(PreguntasModel):
    preguntas: Optional[list[Pregunta]] = Field(default=None, max_length=10)
    titulo: Optional[Annotated[str, Field(min_length=1, max_length=150)]] = None
    descripcion: Optional[Annotated[str, Field(min_length=1, max_length=10000)]] = None
    requisitos: Optional[str] = None
    ubicacion: Optional[Annotated[str, Field(max_length=150)]] = None
    modalidad: Optional[Annotated[str, Field(max_length=50)]] = None
    activa: Optional[bool] = None


class OfertaEmpleoOut(OfertaEmpleoBase):
    formulario_version: int
    id: int
    empresa_id: int
    fecha_publicacion: datetime
    activa: bool

    model_config = ConfigDict(from_attributes=True)


class OfertaEmpleoConEmpresa(OfertaEmpleoOut):
    """Version de la oferta que incluye el nombre de la empresa, para el hub del egresado."""

    nombre_empresa: Annotated[str, Field(min_length=1, max_length=150)]


class Login(InputModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=72)


class SessionOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UsuarioOut


class PostulacionCreate(InputModel):
    oferta_id: int = Field(gt=0)
    formulario_version: int = Field(ge=1)
    telefono: str = Field(default='', max_length=30)
    cv_url: str = Field(default='', max_length=500)
    mensaje: str = Field(default='', max_length=3000)
    respuestas: dict[str, Annotated[str, Field(max_length=3000)]] = Field(default_factory=dict, max_length=10)
    consentimiento: Literal[True]


class PresentacionInput(InputModel):
    presentacion: str = Field(min_length=1, max_length=5000)
