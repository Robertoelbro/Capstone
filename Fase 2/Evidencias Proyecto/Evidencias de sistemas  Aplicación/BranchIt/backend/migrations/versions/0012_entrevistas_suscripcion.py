"""Multiple daily interview sessions for subscribed graduates; free limit in API."""
from alembic import op, context
import sqlalchemy as sa

revision = '0012_entrevistas_suscripcion'
down_revision = '0011_suscripciones'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('entrevistas_ia') as batch:
        batch.add_column(sa.Column('creada', sa.DateTime(), nullable=False, server_default=sa.func.now()))
        batch.drop_constraint('uq_entrevista_usuario_dia', type_='unique')
        batch.create_index('ix_entrevistas_usuario_fecha', ['usuario_id', 'fecha'])


def downgrade():
    if not context.is_offline_mode():
        duplicate = op.get_bind().execute(sa.text(
            'SELECT usuario_id FROM entrevistas_ia GROUP BY usuario_id, fecha HAVING count(*) > 1 LIMIT 1')).first()
        if duplicate:
            raise RuntimeError('No se puede restaurar el límite único sin perder entrevistas. Conserve los datos y revise la reversión.')
    with op.batch_alter_table('entrevistas_ia') as batch:
        batch.drop_index('ix_entrevistas_usuario_fecha')
        batch.create_unique_constraint('uq_entrevista_usuario_dia', ['usuario_id', 'fecha'])
        batch.drop_column('creada')
