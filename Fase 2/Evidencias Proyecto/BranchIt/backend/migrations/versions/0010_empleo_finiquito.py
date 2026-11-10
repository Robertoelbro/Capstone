"""Permanent experience gate, preserving encrypted employment state and legacy records."""
from alembic import op
import sqlalchemy as sa

revision = '0010_empleo_finiquito'
down_revision = '0009_seguimiento_laboral'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('seguimiento_laboral', sa.Column(
        'limite_experiencia', sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade():
    op.drop_column('seguimiento_laboral', 'limite_experiencia')
