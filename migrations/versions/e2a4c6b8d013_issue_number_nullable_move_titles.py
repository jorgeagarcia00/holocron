"""allow empty issue_number; move non-regular numbers into issue_title

Revision ID: e2a4c6b8d013
Revises: d7b2a9c4e815
Create Date: 2026-10-10 09:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e2a4c6b8d013'
down_revision = 'd7b2a9c4e815'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('comic_issue', recreate='always') as batch_op:
        batch_op.alter_column('issue_number', existing_type=sa.String(20), nullable=True)

    conn = op.get_bind()

    # Regular issues keep a number, stored without a leading "#".
    conn.execute(sa.text(
        "UPDATE comic_issue SET issue_number = LTRIM(issue_number, '#') "
        "WHERE designation = 'regular_issue' AND issue_number LIKE '#%'"
    ))

    # Every other type keeps its text in the title; the number goes empty.
    conn.execute(sa.text(
        "UPDATE comic_issue SET issue_title = issue_number "
        "WHERE designation != 'regular_issue' AND issue_title IS NULL "
        "AND issue_number IS NOT NULL AND TRIM(issue_number) != ''"
    ))
    # "TP", "TPB" and "HC" are added automatically at display time, never stored.
    conn.execute(sa.text(
        "UPDATE comic_issue SET issue_title = NULL "
        "WHERE designation = 'collected_edition' "
        "AND UPPER(TRIM(issue_title)) IN ('TP', 'TPB', 'HC')"
    ))
    conn.execute(sa.text(
        "UPDATE comic_issue SET issue_number = NULL WHERE designation != 'regular_issue'"
    ))


def downgrade():
    conn = op.get_bind()
    conn.execute(sa.text(
        "UPDATE comic_issue SET issue_number = COALESCE(NULLIF(issue_title, ''), '1') "
        "WHERE issue_number IS NULL"
    ))
    with op.batch_alter_table('comic_issue', recreate='always') as batch_op:
        batch_op.alter_column('issue_number', existing_type=sa.String(20), nullable=False)
