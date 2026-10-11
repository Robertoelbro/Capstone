"""Structured portfolio data; only explicitly published fields are public."""
from typing import Annotated, Literal
from urllib.parse import urlsplit
from pydantic import BaseModel, ConfigDict, Field, BeforeValidator, model_validator

def clean_url(value):
    value = value.strip()
    if value:
        parsed = urlsplit(value)
        if parsed.scheme not in ('http', 'https') or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError('Utiliza un enlace http o https sin credenciales.')
    return value

URL = Annotated[str, BeforeValidator(clean_url), Field(max_length=1000)]
Label = Annotated[str, Field(min_length=1, max_length=120)]
AssetId = Annotated[str, Field(pattern=r'^[a-f0-9]{32}$')]

class Item(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)

class Skill(Item):
    nombre: Label
    nivel: Literal['Aprendiendo', 'Intermedio', 'Avanzado'] = 'Aprendiendo'

class Certificate(Item):
    nombre: Label
    entidad: str = Field(default='', max_length=150)
    url: URL = ''
    archivo_id: AssetId | None = None

    @model_validator(mode='after')
    def evidence(self):
        if not self.url and not self.archivo_id:
            raise ValueError('Añade un enlace o documento de la certificación.')
        return self

class Project(Item):
    titulo: Label
    descripcion: str = Field(default='', max_length=2000)
    tipo: Literal['Académico', 'Personal'] = 'Académico'
    tecnologias: list[Label] = Field(default_factory=list, max_length=12)
    github_url: URL = ''
    proyecto_url: URL = ''
    video_url: URL = ''
    video_id: AssetId | None = None
    qr_id: AssetId | None = None

class Portfolio(Item):
    titular: str = Field(default='', max_length=160)
    ubicacion: str = Field(default='', max_length=120)
    contacto_email: str = Field(default='', max_length=255)
    contacto_telefono: str = Field(default='', max_length=30)
    disponibilidad: Literal['Sin definir', 'Inmediata', 'En 2 semanas', 'En 1 mes', 'A convenir', 'No disponible'] = 'Sin definir'
    foto_id: AssetId | None = None
    video_id: AssetId | None = None
    video_url: URL = ''
    github_url: URL = ''
    habilidades: list[Skill] = Field(default_factory=list, max_length=20)
    certificaciones: list[Certificate] = Field(default_factory=list, max_length=12)
    proyectos: list[Project] = Field(default_factory=list, max_length=12)
    publico: bool = False
    mostrar_email: bool = False
    mostrar_telefono: bool = False
    tema: Literal['bosque', 'arcilla', 'oceano'] = 'bosque'

    @model_validator(mode='after')
    def email_format(self):
        if self.contacto_email:
            from pydantic import TypeAdapter, EmailStr
            self.contacto_email = str(TypeAdapter(EmailStr).validate_python(self.contacto_email))
        return self

def media_references(data):
    """Map references to expected purpose; don't accept another user's assets."""
    refs = []
    for key, kind in [('foto_id', 'foto'), ('video_id', 'presentacion')]:
        if data.get(key): refs.append((data[key], kind))
    for item in data.get('certificaciones', []):
        if item.get('archivo_id'): refs.append((item['archivo_id'], 'certificado'))
    for item in data.get('proyectos', []):
        for key, kind in [('video_id', 'proyecto'), ('qr_id', 'qr')]:
            if item.get(key): refs.append((item[key], kind))
    return refs

class MediaReserve(Item):
    tipo: Literal['foto', 'presentacion', 'certificado', 'proyecto', 'qr']
    nombre: str = Field(min_length=1, max_length=180)
    mime: Literal['image/jpeg', 'image/png', 'image/webp', 'application/pdf', 'video/mp4', 'video/webm']
    tamano: int = Field(gt=0, le=30 * 1024 * 1024)
    duracion: float | None = Field(default=None, gt=0, le=180, allow_inf_nan=False)
