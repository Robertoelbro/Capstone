"""Preguntas de ofertas, postulaciones cifradas y revocacion de sesiones."""
from alembic import op
import sqlalchemy as sa

revision = '0002_postulaciones'
down_revision = '0001_esquema_inicial'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('usuarios', sa.Column('token_version', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('ofertas_empleo', sa.Column('preguntas', sa.JSON(), nullable=False, server_default=sa.text("'[]'")))
    op.add_column('ofertas_empleo', sa.Column('formulario_version', sa.Integer(), nullable=False, server_default='1'))
    op.create_table('postulaciones',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('oferta_id', sa.Integer(), sa.ForeignKey('ofertas_empleo.id'), nullable=False),
        sa.Column('egresado_id', sa.Integer(), sa.ForeignKey('perfiles_egresado.id'), nullable=False),
        sa.Column('fecha_postulacion', sa.DateTime(), nullable=False),
        sa.Column('datos_cifrados', sa.Text(), nullable=False),
        sa.UniqueConstraint('oferta_id', 'egresado_id', name='uq_postulacion_oferta_egresado'))
    op.create_index('ix_postulaciones_oferta_id', 'postulaciones', ['oferta_id'])
    op.create_index('ix_postulaciones_egresado_id', 'postulaciones', ['egresado_id'])


def downgrade():
    op.drop_table('postulaciones')
    op.drop_column('ofertas_empleo', 'formulario_version')
    op.drop_column('ofertas_empleo', 'preguntas')
    op.drop_column('usuarios', 'token_version')
