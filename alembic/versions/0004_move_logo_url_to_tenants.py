"""
Revision ID: 0004_move_logo_url_to_tenants
Revises: 0003_add_tenant_id_to_documentos_pdf
Create Date: 2026-03-30

Mueve logo_url de tenant_temas a tenants.
El logo es un atributo del tenant, no del tema visual.
"""

revision = '0004_move_logo_url_to_tenants'
down_revision = '0003_tenant_id_docs_pdf'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    # Agregar logo_url a tenants
    op.add_column('tenants', sa.Column('logo_url', sa.String(500), nullable=True))

    # Migrar datos existentes de tenant_temas.logo_url → tenants.logo_url
    op.execute("""
        UPDATE tenants
        SET logo_url = tt.logo_url
        FROM tenant_temas tt
        WHERE tenants.tema_id = tt.id
        AND tt.logo_url IS NOT NULL
    """)

    # Eliminar logo_url de tenant_temas
    op.drop_column('tenant_temas', 'logo_url')


def downgrade():
    op.add_column('tenant_temas', sa.Column('logo_url', sa.String(500), nullable=True))

    op.execute("""
        UPDATE tenant_temas
        SET logo_url = t.logo_url
        FROM tenants t
        WHERE tenant_temas.id = t.tema_id
        AND t.logo_url IS NOT NULL
    """)

    op.drop_column('tenants', 'logo_url')
