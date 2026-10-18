"""Private selection of one application per job."""
from alembic import op
import sqlalchemy as sa

revision = '0006_cierre_convocatorias'
down_revision = '0005_ofertas_completas'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('postulaciones', sa.Column('seleccionada', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.create_index('uq_seleccion_por_oferta', 'postulaciones', ['oferta_id'], unique=True,
                    postgresql_where=sa.text('seleccionada = true'), sqlite_where=sa.text('seleccionada = 1'))


def downgrade():
    op.drop_index('uq_seleccion_por_oferta', table_name='postulaciones')
    op.drop_column('postulaciones', 'seleccionada')
