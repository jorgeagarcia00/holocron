"""add sort_order to role, reseed comics roles

Revision ID: a8a570bd4199
Revises: a1b2c3d4e5f6
Create Date: 2026-05-17 23:57:40.067270

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a8a570bd4199'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


# (department_name, role_name, sort_order)
_ROLES = [
    ('Writers',    'Writer',                10),
    ('Writers',    'Script',                20),
    ('Writers',    'Plot',                  30),
    ('Writers',    'Story',                 40),
    ('Writers',    'Dialogue',              50),
    ('Artists',    'Penciler',              10),
    ('Artists',    'Inker',                 20),
    ('Artists',    'Artist',                30),
    ('Artists',    'Colorist',              40),
    ('Artists',    'Letterer',              50),
    ('Editors',    'Editor',                10),
    ('Editors',    'Senior Editor',         20),
    ('Editors',    'Associate Editor',      30),
    ('Editors',    'Assistant Editor',      40),
    ('Cover',      'Cover Artist',          10),
    ('Cover',      'Cover Penciler',        20),
    ('Cover',      'Cover Inker',           30),
    ('Cover',      'Cover Colorist',        40),
    ('Production', 'Editor-in-Chief',       10),
    ('Production', 'Collection Editor',     20),
    ('Production', 'Book Designer',         30),
    ('Production', 'Production Manager',    40),
    ('Lucasfilm',  'Lucasfilm Editor',      10),
    ('Lucasfilm',  'Lucasfilm Art Director', 20),
    ('Lucasfilm',  'Creative Director',     30),
    ('Lucasfilm',  'Art Director',          40),
    ('Lucasfilm',  'Story Group',           50),
    ('Lucasfilm',  'Creative Art Manager',  60),
    ('Lucasfilm',  'Licensing Manager',     70),
]


def upgrade():
    with op.batch_alter_table('role', schema=None) as batch_op:
        batch_op.add_column(sa.Column('sort_order', sa.Integer(), nullable=True))

    conn = op.get_bind()

    # Clear existing roles (role_name stored as string on credits — no FK breakage)
    conn.execute(sa.text('DELETE FROM role'))

    # Re-insert with sort_order, resolving department_id by name
    for dept_name, role_name, sort_order in _ROLES:
        row = conn.execute(
            sa.text('SELECT id FROM department WHERE name = :n'),
            {'n': dept_name}
        ).fetchone()
        if row:
            conn.execute(
                sa.text('INSERT INTO role (name, department_id, sort_order, created_at) '
                        'VALUES (:name, :dept_id, :sort_order, CURRENT_TIMESTAMP)'),
                {'name': role_name, 'dept_id': row[0], 'sort_order': sort_order}
            )


def downgrade():
    with op.batch_alter_table('role', schema=None) as batch_op:
        batch_op.drop_column('sort_order')
