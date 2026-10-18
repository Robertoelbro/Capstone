"""Persistent private notification inbox."""
from alembic import op
import sqlalchemy as sa

revision = '0007_notificaciones'
down_revision = '0006_cierre_convocatorias'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('notificaciones',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('usuario_id', sa.Integer(), sa.ForeignKey('usuarios.id'), nullable=False),
        sa.Column('mensaje', sa.String(400), nullable=False),
        sa.Column('destino', sa.String(200), nullable=False),
        sa.Column('leida', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('creada', sa.DateTime(), nullable=False, server_default=sa.func.now()))
    op.create_index('ix_notificaciones_usuario_id', 'notificaciones', ['usuario_id'])


def downgrade():
    op.drop_table('notificaciones')
