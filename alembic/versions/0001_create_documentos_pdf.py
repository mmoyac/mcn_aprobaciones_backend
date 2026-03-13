"""
Revision ID: 0001_create_documentos_pdf
Revises: None
Create Date: 2025-12-17
"""

revision = '0001_docs_pdf'
down_revision = None
branch_labels = None
depends_on = None
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'documentos_pdf',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True, index=True),
        sa.Column('tipo', sa.SmallInteger(), nullable=False, comment='1=presupuesto, 2=orden de compra'),
        sa.Column('numero', sa.BigInteger(), nullable=False),
        sa.Column('fecha_creacion', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('pdf', sa.LargeBinary(), nullable=False)
    )

def downgrade():
    op.drop_table('documentos_pdf')
