"""
Revision ID: 0003_add_tenant_id_to_documentos_pdf
Revises: 0002_create_tenant_tables
Create Date: 2026-03-13

Agrega tenant_id FK a documentos_pdf para aislar PDFs por tenant.
Los registros existentes se asignan al tenant con id=1 (primer tenant).
"""

revision = '0003_tenant_id_docs_pdf'
down_revision = '0002_tenant_tables'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    # 1. Agregar columna nullable primero
    op.add_column('documentos_pdf',
        sa.Column('tenant_id', sa.Integer(), nullable=True)
    )
    # 2. Asignar tenant_id=1 a todos los registros existentes
    op.execute("UPDATE documentos_pdf SET tenant_id = 1 WHERE tenant_id IS NULL")
    # 3. Agregar FK y NOT NULL
    op.alter_column('documentos_pdf', 'tenant_id', nullable=False)
    op.create_foreign_key(
        'fk_documentos_pdf_tenant_id',
        'documentos_pdf', 'tenants',
        ['tenant_id'], ['id']
    )
    op.create_index('ix_documentos_pdf_tenant_id', 'documentos_pdf', ['tenant_id'])


def downgrade():
    op.drop_index('ix_documentos_pdf_tenant_id', table_name='documentos_pdf')
    op.drop_constraint('fk_documentos_pdf_tenant_id', 'documentos_pdf', type_='foreignkey')
    op.drop_column('documentos_pdf', 'tenant_id')
