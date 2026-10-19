import enum
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    String,
    Text,
    Boolean,
    DateTime,
    Date,
    ForeignKey,
    Enum,
    JSON,
    UniqueConstraint,
    Index,
    text,
)
from sqlalchemy.orm import relationship

from .database import Base


class TipoUsuario(str, enum.Enum):
    egresado = "egresado"
    empresa = "empresa"


class Usuario(Base):
    """Cuenta de acceso: puede ser un egresado o una empresa."""

    __tablename__ = "usuarios"
    __table_args__ = (Index('uq_usuarios_rut', 'rut', unique=True),)

    id = Column(Integer, primary_key=True, index=True)
    rut = Column(String(12), nullable=True)
    telefono = Column(String(30), nullable=True)
    fecha_identidad = Column(Date, nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    tipo = Column(Enum(TipoUsuario), nullable=False)
    fecha_registro = Column(DateTime, default=datetime.utcnow, nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
    token_version = Column(Integer, default=0, nullable=False)
    archivos = relationship('ArchivoPortfolio', cascade='all, delete-orphan')
    notificaciones = relationship('Notificacion', cascade='all, delete-orphan')
    entrevistas_ia = relationship('EntrevistaIA', cascade='all, delete-orphan')

    perfil_egresado = relationship(
        "PerfilEgresado",
        back_populates="usuario",
        uselist=False,
        cascade="all, delete-orphan",
    )
    perfil_empresa = relationship(
        "PerfilEmpresa",
        back_populates="usuario",
        uselist=False,
        cascade="all, delete-orphan",
    )


class PerfilEgresado(Base):
    """Datos de presentacion del egresado (lo que se muestra en su perfil)."""

    __tablename__ = "perfiles_egresado"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), unique=True, nullable=False)

    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    carrera = Column(String(150))
    anio_egreso = Column(Integer)
    presentacion = Column(Text)  # texto de presentacion / bio
    linkedin_url = Column(String(255))
    foto_url = Column(String(255))
    portfolio = Column(JSON, default=dict, nullable=False)

    usuario = relationship("Usuario", back_populates="perfil_egresado")
    postulaciones = relationship("Postulacion", back_populates="egresado", cascade="all, delete-orphan")


class PerfilEmpresa(Base):
    """Datos de presentacion de la empresa."""

    __tablename__ = "perfiles_empresa"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), unique=True, nullable=False)

    nombre_empresa = Column(String(150), nullable=False)
    rubro = Column(String(150))
    descripcion = Column(Text)
    sitio_web = Column(String(255))
    logo_url = Column(String(255))
    foto_id = Column(String(32), ForeignKey("archivos_portfolio.id"), nullable=True)

    usuario = relationship("Usuario", back_populates="perfil_empresa")
    ofertas = relationship(
        "OfertaEmpleo", back_populates="empresa", cascade="all, delete-orphan"
    )


class OfertaEmpleo(Base):
    """Oferta de empleo publicada por una empresa."""

    __tablename__ = "ofertas_empleo"
    __table_args__ = (Index('uq_ofertas_demo_clave', 'demo_clave', unique=True),)

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(
        Integer, ForeignKey("perfiles_empresa.id"), nullable=False
    )

    titulo = Column(String(150), nullable=False)
    descripcion = Column(Text, nullable=False)
    requisitos = Column(Text)
    ubicacion = Column(String(150))
    modalidad = Column(String(50))  # ej: presencial, remoto, hibrido
    fecha_publicacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    activa = Column(Boolean, default=True, nullable=False)
    preguntas = Column(JSON, default=list, nullable=False)
    formulario_version = Column(Integer, default=1, nullable=False)
    categoria = Column(String(80), nullable=False, default='General')
    demo_clave = Column(String(80))
    sueldo = Column(BigInteger, nullable=True)
    funciones = Column(Text, nullable=True)
    perfiles_deseados = Column(JSON, nullable=True)
    condiciones_laborales = Column(Text, nullable=True)
    adaptada_discapacidad = Column(Boolean, nullable=True)

    empresa = relationship("PerfilEmpresa", back_populates="ofertas")
    postulaciones = relationship("Postulacion", back_populates="oferta")


class Postulacion(Base):
    __tablename__ = 'postulaciones'
    __table_args__ = (
        UniqueConstraint('oferta_id', 'egresado_id', name='uq_postulacion_oferta_egresado'),
        Index('uq_seleccion_por_oferta', 'oferta_id', unique=True,
              postgresql_where=text('seleccionada = true'), sqlite_where=text('seleccionada = 1')),
    )

    id = Column(Integer, primary_key=True)
    oferta_id = Column(Integer, ForeignKey('ofertas_empleo.id'), nullable=False, index=True)
    egresado_id = Column(Integer, ForeignKey('perfiles_egresado.id'), nullable=False, index=True)
    fecha_postulacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    datos_cifrados = Column(Text, nullable=False)
    seleccionada = Column(Boolean, default=False, nullable=False)
    oferta = relationship('OfertaEmpleo', back_populates='postulaciones')
    egresado = relationship('PerfilEgresado', back_populates='postulaciones')


class EntrevistaIA(Base):
    __tablename__ = 'entrevistas_ia'
    __table_args__ = (UniqueConstraint('usuario_id', 'fecha', name='uq_entrevista_usuario_dia'),)
    id = Column(String(32), primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    fecha = Column(Date, nullable=False)
    oferta_id = Column(Integer, ForeignKey('ofertas_empleo.id', ondelete='SET NULL'), nullable=True)
    datos_cifrados = Column(Text, nullable=False)
    turnos = Column(Integer, nullable=False, default=0)


class Notificacion(Base):
    __tablename__ = 'notificaciones'
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False, index=True)
    mensaje = Column(String(400), nullable=False)
    destino = Column(String(200), nullable=False)
    leida = Column(Boolean, default=False, nullable=False)
    creada = Column(DateTime, default=datetime.utcnow, nullable=False)


class ArchivoPortfolio(Base):
    __tablename__ = 'archivos_portfolio'
    id = Column(String(32), primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False, index=True)
    tipo = Column(String(20), nullable=False)
    nombre = Column(String(180), nullable=False)
    mime = Column(String(80), nullable=False)
    tamano = Column(Integer, nullable=False)
    duracion = Column(Integer)
    pathname = Column(String(255), nullable=False, unique=True)
    verificado = Column(Boolean, nullable=False, default=False)
    creado = Column(DateTime, default=datetime.utcnow, nullable=False)
