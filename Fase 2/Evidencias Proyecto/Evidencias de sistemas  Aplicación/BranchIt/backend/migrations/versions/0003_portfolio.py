"""Portafolio, archivos privados y categorías de empleo."""
from alembic import op
import sqlalchemy as sa

revision = '0003_portfolio'
down_revision = '0002_postulaciones'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('perfiles_egresado', sa.Column('portfolio', sa.JSON(), nullable=False, server_default=sa.text("'{}'")))
    op.add_column('ofertas_empleo', sa.Column('categoria', sa.String(80), nullable=False, server_default='General'))
    op.add_column('ofertas_empleo', sa.Column('demo_clave', sa.String(80)))
    op.create_index('uq_ofertas_demo_clave', 'ofertas_empleo', ['demo_clave'], unique=True)
    op.create_table('archivos_portfolio',
        sa.Column('id', sa.String(32), primary_key=True),
        sa.Column('usuario_id', sa.Integer(), sa.ForeignKey('usuarios.id'), nullable=False),
        sa.Column('tipo', sa.String(20), nullable=False),
        sa.Column('nombre', sa.String(180), nullable=False),
        sa.Column('mime', sa.String(80), nullable=False),
        sa.Column('tamano', sa.Integer(), nullable=False),
        sa.Column('duracion', sa.Integer()),
        sa.Column('pathname', sa.String(255), nullable=False, unique=True),
        sa.Column('verificado', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('creado', sa.DateTime(), nullable=False))
    op.create_index('ix_archivos_portfolio_usuario_id', 'archivos_portfolio', ['usuario_id'])

def downgrade():
    op.drop_table('archivos_portfolio')
    op.drop_index('uq_ofertas_demo_clave', table_name='ofertas_empleo')
    op.drop_column('ofertas_empleo', 'demo_clave')
    op.drop_column('ofertas_empleo', 'categoria')
    op.drop_column('perfiles_egresado', 'portfolio')
