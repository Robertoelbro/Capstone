import enum
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    Enum,
)
from sqlalchemy.orm import relationship

from .database import Base


class TipoUsuario(str, enum.Enum):
    egresado = "egresado"
    empresa = "empresa"


class Usuario(Base):
    """Cuenta de acceso: puede ser un egresado o una empresa."""

    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    tipo = Column(Enum(TipoUsuario), nullable=False)
    fecha_registro = Column(DateTime, default=datetime.utcnow, nullable=False)
    activo = Column(Boolean, default=True, nullable=False)

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

    usuario = relationship("Usuario", back_populates="perfil_egresado")


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

    usuario = relationship("Usuario", back_populates="perfil_empresa")
    ofertas = relationship(
        "OfertaEmpleo", back_populates="empresa", cascade="all, delete-orphan"
    )


class OfertaEmpleo(Base):
    """Oferta de empleo publicada por una empresa."""

    __tablename__ = "ofertas_empleo"

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

    empresa = relationship("PerfilEmpresa", back_populates="ofertas")
