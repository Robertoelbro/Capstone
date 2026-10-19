"""One resumable interview per graduate and Santiago calendar day."""
from alembic import op
import sqlalchemy as sa

revision = '0008_entrevista_diaria'
down_revision = '0007_notificaciones'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('entrevistas_ia',
        sa.Column('id', sa.String(32), primary_key=True),
        sa.Column('usuario_id', sa.Integer(), sa.ForeignKey('usuarios.id'), nullable=False),
        sa.Column('fecha', sa.Date(), nullable=False),
        sa.Column('oferta_id', sa.Integer(), sa.ForeignKey('ofertas_empleo.id', ondelete='SET NULL'), nullable=True),
        sa.Column('datos_cifrados', sa.Text(), nullable=False),
        sa.Column('turnos', sa.Integer(), nullable=False),
        sa.UniqueConstraint('usuario_id', 'fecha', name='uq_entrevista_usuario_dia'))


def downgrade():
    op.drop_table('entrevistas_ia')
