"""add Senior Editor to Production roles

Revision ID: d7b2a9c4e815
Revises: c3e1f0a7b201
Create Date: 2026-10-09 12:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd7b2a9c4e815'
down_revision = 'c3e1f0a7b201'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    dept = conn.execute(
        sa.text("SELECT id FROM department WHERE name = 'Production' AND pillar = 'comics'")
    ).fetchone()
    if dept is None:
        return
    exists = conn.execute(
        sa.text("SELECT 1 FROM role WHERE name = 'Senior Editor' AND department_id = :d"),
        {'d': dept[0]}
    ).fetchone()
    if exists is None:
        conn.execute(
            sa.text('INSERT INTO role (name, department_id, sort_order, created_at) '
                    "VALUES ('Senior Editor', :d, 50, CURRENT_TIMESTAMP)"),
            {'d': dept[0]}
        )


def downgrade():
    conn = op.get_bind()
    conn.execute(sa.text(
        "DELETE FROM role WHERE name = 'Senior Editor' AND department_id = "
        "(SELECT id FROM department WHERE name = 'Production' AND pillar = 'comics')"))
