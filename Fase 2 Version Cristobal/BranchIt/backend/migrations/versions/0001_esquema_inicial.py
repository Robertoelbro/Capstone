"""esquema inicial: usuarios, perfiles egresado/empresa, ofertas de empleo

Revision ID: 0001_esquema_inicial
Revises:
Create Date: 2026-09-12

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0001_esquema_inicial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    tipo_usuario = sa.Enum("egresado", "empresa", name="tipousuario")
    tipo_usuario.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True, index=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("tipo", tipo_usuario, nullable=False),
        sa.Column("fecha_registro", sa.DateTime(), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.true()),
    )

    op.create_table(
        "perfiles_egresado",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuarios.id"), nullable=False, unique=True),
        sa.Column("nombre", sa.String(length=100), nullable=False),
        sa.Column("apellido", sa.String(length=100), nullable=False),
        sa.Column("carrera", sa.String(length=150), nullable=True),
        sa.Column("anio_egreso", sa.Integer(), nullable=True),
        sa.Column("presentacion", sa.Text(), nullable=True),
        sa.Column("linkedin_url", sa.String(length=255), nullable=True),
        sa.Column("foto_url", sa.String(length=255), nullable=True),
    )

    op.create_table(
        "perfiles_empresa",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuarios.id"), nullable=False, unique=True),
        sa.Column("nombre_empresa", sa.String(length=150), nullable=False),
        sa.Column("rubro", sa.String(length=150), nullable=True),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("sitio_web", sa.String(length=255), nullable=True),
        sa.Column("logo_url", sa.String(length=255), nullable=True),
    )

    op.create_table(
        "ofertas_empleo",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("empresa_id", sa.Integer(), sa.ForeignKey("perfiles_empresa.id"), nullable=False),
        sa.Column("titulo", sa.String(length=150), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=False),
        sa.Column("requisitos", sa.Text(), nullable=True),
        sa.Column("ubicacion", sa.String(length=150), nullable=True),
        sa.Column("modalidad", sa.String(length=50), nullable=True),
        sa.Column("fecha_publicacion", sa.DateTime(), nullable=False),
        sa.Column("activa", sa.Boolean(), nullable=False, server_default=sa.true()),
    )


def downgrade() -> None:
    op.drop_table("ofertas_empleo")
    op.drop_table("perfiles_empresa")
    op.drop_table("perfiles_egresado")
    op.drop_table("usuarios")

    tipo_usuario = sa.Enum("egresado", "empresa", name="tipousuario")
    tipo_usuario.drop(op.get_bind(), checkfirst=True)
