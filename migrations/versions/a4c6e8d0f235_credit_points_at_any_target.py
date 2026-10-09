"""credit points at any target (target_type + target_id); add note

Revision ID: a4c6e8d0f235
Revises: f3b5d7c9e124
Create Date: 2026-10-10 10:00:00.000000

Credits used to carry segment_id / issue_id. They now say what they point at with
target_type ('comic_segment', 'comic_issue'; later 'tv_episode', 'film', ...) and
target_id, so one credit list and one creator page can serve every pillar.
Like series_membership, the target is a polymorphic reference with no FK.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a4c6e8d0f235'
down_revision = 'f3b5d7c9e124'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('credit', recreate='always') as batch_op:
        batch_op.add_column(sa.Column('target_type', sa.String(30), nullable=True))
        batch_op.add_column(sa.Column('target_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('note', sa.Text(), nullable=True))

    conn = op.get_bind()
    conn.execute(sa.text(
        "UPDATE credit SET target_type = 'comic_segment', target_id = segment_id "
        "WHERE segment_id IS NOT NULL"
    ))
    conn.execute(sa.text(
        "UPDATE credit SET target_type = 'comic_issue', target_id = issue_id "
        "WHERE segment_id IS NULL AND issue_id IS NOT NULL"
    ))
    orphans = conn.execute(sa.text(
        "SELECT COUNT(*) FROM credit WHERE target_type IS NULL OR target_id IS NULL"
    )).scalar()
    if orphans:
        raise RuntimeError(f'{orphans} credit(s) point at neither a segment nor an issue; '
                           'nothing was dropped. Fix or remove them and re-run.')

    with op.batch_alter_table('credit', recreate='always') as batch_op:
        batch_op.drop_column('segment_id')
        batch_op.drop_column('issue_id')
        batch_op.alter_column('target_type', existing_type=sa.String(30), nullable=False)
        batch_op.alter_column('target_id', existing_type=sa.Integer(), nullable=False)
        batch_op.create_index('ix_credit_target', ['target_type', 'target_id'])


def downgrade():
    with op.batch_alter_table('credit', recreate='always') as batch_op:
        batch_op.drop_index('ix_credit_target')
        batch_op.add_column(sa.Column('segment_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('issue_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_credit_segment', 'comic_segment', ['segment_id'], ['id'])
        batch_op.create_foreign_key('fk_credit_issue', 'comic_issue', ['issue_id'], ['id'])

    conn = op.get_bind()
    conn.execute(sa.text(
        "UPDATE credit SET segment_id = target_id WHERE target_type = 'comic_segment'"
    ))
    conn.execute(sa.text(
        "UPDATE credit SET issue_id = target_id WHERE target_type = 'comic_issue'"
    ))

    with op.batch_alter_table('credit', recreate='always') as batch_op:
        batch_op.drop_column('target_type')
        batch_op.drop_column('target_id')
        batch_op.drop_column('note')
