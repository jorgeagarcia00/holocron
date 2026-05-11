"""rename era_id to canon_era_id, add legends_era_id on comic_series

Revision ID: a1b2c3d4e5f6
Revises: 3189978d7262
Create Date: 2026-05-11

"""
from alembic import op
import sqlalchemy as sa


revision = 'a1b2c3d4e5f6'
down_revision = '3189978d7262'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('comic_series', recreate='always') as batch_op:
        batch_op.alter_column('era_id', new_column_name='canon_era_id')
        batch_op.add_column(sa.Column('legends_era_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            'fk_comic_series_legends_era', 'era', ['legends_era_id'], ['id']
        )


def downgrade():
    with op.batch_alter_table('comic_series', recreate='always') as batch_op:
        batch_op.drop_constraint('fk_comic_series_legends_era', type_='foreignkey')
        batch_op.drop_column('legends_era_id')
        batch_op.alter_column('canon_era_id', new_column_name='era_id')
