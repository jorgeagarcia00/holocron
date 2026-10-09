"""add optional volume to comic_series

Revision ID: f3b5d7c9e124
Revises: e2a4c6b8d013
Create Date: 2026-10-10 09:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f3b5d7c9e124'
down_revision = 'e2a4c6b8d013'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('comic_series', recreate='always') as batch_op:
        batch_op.add_column(sa.Column('volume', sa.Integer(), nullable=True))


def downgrade():
    with op.batch_alter_table('comic_series', recreate='always') as batch_op:
        batch_op.drop_column('volume')
