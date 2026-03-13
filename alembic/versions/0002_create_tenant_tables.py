"""
Revision ID: 0002_create_tenant_tables
Revises: 0001_create_documentos_pdf
Create Date: 2026-03-13

Crea las tablas de multitenancy:
- tenant_temas: paleta de colores (maestra)
- tenants: registro de empresas/clientes
- tenant_conexiones: credenciales de BD MySQL por tenant
"""

revision = '0002_tenant_tables'
down_revision = '0001_docs_pdf'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    # 1. Maestra de paletas de colores
    op.create_table(
        'tenant_temas',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('nombre', sa.String(100), nullable=False),
        sa.Column('color_primary', sa.String(7), nullable=False, server_default='#5EC8F2'),
        sa.Column('color_secondary', sa.String(7), nullable=False, server_default='#45A29A'),
        sa.Column('color_background', sa.String(7), nullable=False, server_default='#0F172A'),
        sa.Column('color_surface', sa.String(7), nullable=False, server_default='#1E293B'),
        sa.Column('color_text', sa.String(7), nullable=False, server_default='#F8FAFC'),
        sa.Column('logo_url', sa.String(500), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    # 2. Registro de tenants
    op.create_table(
        'tenants',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('slug', sa.String(50), nullable=False, unique=True),
        sa.Column('nombre', sa.String(200), nullable=False),
        sa.Column('dominio', sa.String(200), nullable=False, unique=True),
        sa.Column('tema_id', sa.Integer(), sa.ForeignKey('tenant_temas.id'), nullable=False),
        sa.Column('activo', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_index('ix_tenants_slug', 'tenants', ['slug'])
    op.create_index('ix_tenants_dominio', 'tenants', ['dominio'])

    # 3. Credenciales de conexión MySQL por tenant
    op.create_table(
        'tenant_conexiones',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id'), nullable=False, unique=True),
        sa.Column('db_host', sa.String(200), nullable=False),
        sa.Column('db_port', sa.Integer(), nullable=False, server_default='3306'),
        sa.Column('db_name', sa.String(100), nullable=False),
        sa.Column('db_user', sa.String(100), nullable=False),
        sa.Column('db_password', sa.String(256), nullable=False),
    )


def downgrade():
    op.drop_table('tenant_conexiones')
    op.drop_index('ix_tenants_dominio', table_name='tenants')
    op.drop_index('ix_tenants_slug', table_name='tenants')
    op.drop_table('tenants')
    op.drop_table('tenant_temas')
