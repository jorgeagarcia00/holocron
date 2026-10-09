"""remove is_uncredited from character_appearance

Revision ID: b5d7f9a1c346
Revises: a4c6e8d0f235
Create Date: 2026-10-10 10:30:00.000000

Only creators can be uncredited (PRD §2.7); characters have no uncredited flag.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b5d7f9a1c346'
down_revision = 'a4c6e8d0f235'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('character_appearance', recreate='always') as batch_op:
        batch_op.drop_column('is_uncredited')


def downgrade():
    with op.batch_alter_table('character_appearance', recreate='always') as batch_op:
        batch_op.add_column(sa.Column('is_uncredited', sa.Boolean(), nullable=False,
                                      server_default=sa.false()))
