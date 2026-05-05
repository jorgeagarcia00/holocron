"""add era sort_order and reseed with PRD §5.4 data

Revision ID: f1a2b3c4d5e6
Revises: b067ab31b604
Create Date: 2026-05-05 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'f1a2b3c4d5e6'
down_revision = 'b067ab31b604'
branch_labels = None
depends_on = None

ERA_DATA = [
    # Canon eras
    ('Dawn of the Jedi',            'canon',   10),
    ('The Old Republic',            'canon',   20),
    ('The High Republic',           'canon',   30),
    ('Fall of the Jedi',            'canon',   40),
    ('Reign of the Empire',         'canon',   50),
    ('Age of Rebellion',            'canon',   60),
    ('The New Republic',            'canon',   70),
    ('Rise of the First Order',     'canon',   80),
    ('New Jedi Order',              'canon',   90),
    ('Visions (Non-Continuity)',    'canon',  999),
    # Legends eras
    ('Before the Republic',         'legends', 10),
    ('The Old Republic',            'legends', 20),
    ('Rise of the Empire',          'legends', 30),
    ('The Rebellion Era',           'legends', 40),
    ('The New Republic',            'legends', 50),
    ('The New Jedi Order',          'legends', 60),
    ('Legacy Era',                  'legends', 70),
    ('Infinities (Non-Continuity)', 'legends', 999),
]

era_table = sa.table(
    'era',
    sa.column('name', sa.String),
    sa.column('continuity', sa.String),
    sa.column('in_universe_date_start', sa.String),
    sa.column('in_universe_date_end', sa.String),
    sa.column('sort_order', sa.Integer),
)


def upgrade():
    op.add_column('era', sa.Column('sort_order', sa.Integer(), nullable=True))
    op.execute('DELETE FROM era')
    op.bulk_insert(era_table, [
        {
            'name': name,
            'continuity': continuity,
            'in_universe_date_start': None,
            'in_universe_date_end': None,
            'sort_order': sort_order,
        }
        for name, continuity, sort_order in ERA_DATA
    ])


def downgrade():
    op.drop_column('era', 'sort_order')
