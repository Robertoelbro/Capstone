"""Webpay Plus integration orders and idempotent entitlement fulfillment."""
from alembic import op
import sqlalchemy as sa

revision = '0013_pagos_webpay'
down_revision = '0012_entrevistas_suscripcion'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('pagos_webpay',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('usuario_id', sa.Integer(), sa.ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False),
        sa.Column('request_id', sa.String(36), nullable=False),
        sa.Column('buy_order', sa.String(26), nullable=False, unique=True),
        sa.Column('session_id', sa.String(61), nullable=False),
        sa.Column('monto_clp', sa.Integer(), nullable=False),
        sa.Column('entorno', sa.String(16), nullable=False),
        sa.Column('estado', sa.String(16), nullable=False),
        sa.Column('token_digest', sa.String(64), nullable=True, unique=True),
        sa.Column('datos_cifrados', sa.Text(), nullable=True),
        sa.Column('creada', sa.DateTime(timezone=True), nullable=False),
        sa.Column('actualizada', sa.DateTime(timezone=True), nullable=False),
        sa.Column('confirmada', sa.DateTime(timezone=True), nullable=True),
        sa.Column('vigente_hasta', sa.DateTime(timezone=True), nullable=True),
        sa.Column('beneficio_aplicado', sa.Boolean(), nullable=False),
        sa.UniqueConstraint('usuario_id', 'request_id', name='uq_pago_solicitud_usuario'),
        sa.CheckConstraint('monto_clp = 2990', name='ck_pago_monto'),
        sa.CheckConstraint("entorno = 'integration'", name='ck_pago_integracion'))
    op.create_index('ix_pagos_webpay_usuario_id', 'pagos_webpay', ['usuario_id'])


def downgrade():
    op.drop_index('ix_pagos_webpay_usuario_id', table_name='pagos_webpay')
    op.drop_table('pagos_webpay')
