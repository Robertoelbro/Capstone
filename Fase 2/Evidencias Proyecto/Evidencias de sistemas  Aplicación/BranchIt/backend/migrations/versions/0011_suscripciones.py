"""Subscription entitlement storage; checkout remains disabled."""
from alembic import op
import sqlalchemy as sa

revision = '0011_suscripciones'
down_revision = '0010_empleo_finiquito'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('suscripciones',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('usuario_id', sa.Integer(), sa.ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('estado', sa.String(12), nullable=False),
        sa.Column('vigente_hasta', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("estado IN ('inactiva', 'activa')", name='ck_suscripcion_estado'))


def downgrade():
    op.drop_table('suscripciones')
