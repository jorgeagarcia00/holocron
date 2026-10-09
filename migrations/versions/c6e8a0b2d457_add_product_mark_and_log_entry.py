"""add product_mark and log_entry (the personal layer)

Revision ID: c6e8a0b2d457
Revises: b5d7f9a1c346
Create Date: 2026-10-10 11:00:00.000000

Two empty tables that can point at any product. Nothing reads or writes them yet.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c6e8a0b2d457'
down_revision = 'b5d7f9a1c346'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'product_mark',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_type', sa.String(30), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('mark', sa.String(10), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('product_type', 'product_id', 'mark',
                            name='uq_product_mark_product_mark'),
    )
    op.create_table(
        'log_entry',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_type', sa.String(30), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('logged_on', sa.Date(), nullable=False),
        sa.Column('read_before', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_log_entry_product', 'log_entry', ['product_type', 'product_id'])


def downgrade():
    op.drop_index('ix_log_entry_product', table_name='log_entry')
    op.drop_table('log_entry')
    op.drop_table('product_mark')
