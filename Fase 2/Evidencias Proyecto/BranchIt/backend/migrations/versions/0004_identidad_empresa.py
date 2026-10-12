"""Registration identity and company photo; existing accounts stay valid."""
from alembic import op
import sqlalchemy as sa

revision = '0004_identidad_empresa'
down_revision = '0003_portfolio'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('usuarios', sa.Column('rut', sa.String(12), nullable=True))
    op.add_column('usuarios', sa.Column('telefono', sa.String(30), nullable=True))
    op.add_column('usuarios', sa.Column('fecha_identidad', sa.Date(), nullable=True))
    op.create_index('uq_usuarios_rut', 'usuarios', ['rut'], unique=True)
    with op.batch_alter_table('perfiles_empresa') as batch:
        batch.add_column(sa.Column('foto_id', sa.String(32), nullable=True))
        batch.create_foreign_key('fk_empresa_foto', 'archivos_portfolio', ['foto_id'], ['id'])

def downgrade():
    with op.batch_alter_table('perfiles_empresa') as batch:
        batch.drop_constraint('fk_empresa_foto', type_='foreignkey')
        batch.drop_column('foto_id')
    op.drop_index('uq_usuarios_rut', table_name='usuarios')
    op.drop_column('usuarios', 'fecha_identidad')
    op.drop_column('usuarios', 'telefono')
    op.drop_column('usuarios', 'rut')
