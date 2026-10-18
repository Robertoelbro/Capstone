"""Offer details, nullable to preserve existing published jobs."""
from alembic import op
import sqlalchemy as sa

revision = '0005_ofertas_completas'
down_revision = '0004_identidad_empresa'
branch_labels = None
depends_on = None


def upgrade():
    for column in (
        sa.Column('sueldo', sa.BigInteger(), nullable=True),
        sa.Column('funciones', sa.Text(), nullable=True),
        sa.Column('perfiles_deseados', sa.JSON(), nullable=True),
        sa.Column('condiciones_laborales', sa.Text(), nullable=True),
        sa.Column('adaptada_discapacidad', sa.Boolean(), nullable=True),
    ):
        op.add_column('ofertas_empleo', column)


def downgrade():
    for name in ('adaptada_discapacidad', 'condiciones_laborales', 'perfiles_deseados', 'funciones', 'sueldo'):
        op.drop_column('ofertas_empleo', name)
