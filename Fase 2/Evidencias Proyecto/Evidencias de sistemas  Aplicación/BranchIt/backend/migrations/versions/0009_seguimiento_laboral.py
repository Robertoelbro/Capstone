"""Private employment follow-up and voluntary job-search pause."""
from alembic import op
import sqlalchemy as sa

revision = '0009_seguimiento_laboral'
down_revision = '0008_entrevista_diaria'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('seguimiento_laboral',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('usuario_id', sa.Integer(), sa.ForeignKey('usuarios.id'), nullable=False, unique=True),
        sa.Column('situacion', sa.String(20), nullable=False),
        sa.Column('busqueda_activa', sa.Boolean(), nullable=False),
        sa.Column('datos_cifrados', sa.Text(), nullable=False),
        sa.Column('actualizado', sa.DateTime(), nullable=False))


def downgrade():
    op.drop_table('seguimiento_laboral')
