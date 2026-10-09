"""rename Visions and Infinities eras (drop "(Non-Continuity)")

Revision ID: c3e1f0a7b201
Revises: a8a570bd4199
Create Date: 2026-10-09 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c3e1f0a7b201'
down_revision = 'a8a570bd4199'
branch_labels = None
depends_on = None


_RENAMES = [
    ('Visions (Non-Continuity)',    'Visions'),
    ('Infinities (Non-Continuity)', 'Infinities'),
]


def upgrade():
    conn = op.get_bind()
    for old, new in _RENAMES:
        conn.execute(sa.text('UPDATE era SET name = :new WHERE name = :old'),
                     {'old': old, 'new': new})


def downgrade():
    conn = op.get_bind()
    for old, new in _RENAMES:
        conn.execute(sa.text('UPDATE era SET name = :old WHERE name = :new'),
                     {'old': old, 'new': new})
