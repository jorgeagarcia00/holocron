from sqlalchemy import inspect as sa_inspect, text
from app.extensions import db


# (name, continuity, sort_order) — matches PRD §5.4
ERA_DATA = [
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
    ('Before the Republic',         'legends', 10),
    ('The Old Republic',            'legends', 20),
    ('Rise of the Empire',          'legends', 30),
    ('The Rebellion Era',           'legends', 40),
    ('The New Republic',            'legends', 50),
    ('The New Jedi Order',          'legends', 60),
    ('Legacy Era',                  'legends', 70),
    ('Infinities (Non-Continuity)', 'legends', 999),
]

COMICS_DEPARTMENTS = [
    ('Writers',    'comics', 'story'),
    ('Artists',    'comics', 'story'),
    ('Editors',    'comics', 'story'),
    ('Cover',      'comics', 'product'),
    ('Production', 'comics', 'product'),
    ('Lucasfilm',  'comics', 'product'),
]

# (department_name, role_name) — seeded on first run
COMICS_ROLES = [
    ('Writers',    'Writer'),
    ('Writers',    'Script'),
    ('Writers',    'Plot'),
    ('Writers',    'Story'),
    ('Writers',    'Dialogue'),
    ('Artists',    'Penciler'),
    ('Artists',    'Inker'),
    ('Artists',    'Artist'),
    ('Artists',    'Colorist'),
    ('Artists',    'Letterer'),
    ('Editors',    'Editor'),
    ('Editors',    'Assistant Editor'),
    ('Editors',    'Associate Editor'),
    ('Editors',    'Senior Editor'),
    ('Cover',      'Cover Artist'),
    ('Cover',      'Cover Penciler'),
    ('Cover',      'Cover Inker'),
    ('Cover',      'Cover Colorist'),
    ('Production', 'Editor-in-Chief'),
    ('Production', 'Collection Editor'),
    ('Production', 'Book Designer'),
    ('Production', 'Production Manager'),
    ('Production', 'Senior Editor'),
    ('Lucasfilm',  'Lucasfilm Editor'),
    ('Lucasfilm',  'Lucasfilm Art Director'),
    ('Lucasfilm',  'Licensing Manager'),
    ('Lucasfilm',  'Story Group Consultant'),
]


def _tables_exist(engine, *names):
    existing = sa_inspect(engine).get_table_names()
    return all(n in existing for n in names)


def _row_count(table_name):
    """Raw SQL count — safe to call before migrations complete."""
    return db.session.execute(text(f'SELECT COUNT(*) FROM {table_name}')).scalar()


def seed_all(flask_app):
    from app.models.preferences import UserPreferences
    from app.models.reference import Era, Department, Role

    with flask_app.app_context():
        engine = db.engine

        if _tables_exist(engine, 'user_preferences'):
            if _row_count('user_preferences') == 0:
                db.session.add(UserPreferences(continuity_filter='both'))
                db.session.commit()

        if _tables_exist(engine, 'era'):
            if _row_count('era') == 0:
                for name, continuity, sort_order in ERA_DATA:
                    db.session.add(Era(name=name, continuity=continuity, sort_order=sort_order))
                db.session.commit()

        if _tables_exist(engine, 'department'):
            if _row_count('department') == 0:
                for name, pillar, scope in COMICS_DEPARTMENTS:
                    db.session.add(Department(name=name, pillar=pillar, scope=scope))
                db.session.commit()

        if _tables_exist(engine, 'role'):
            if _row_count('role') == 0:
                dept_map = {d.name: d.id for d in Department.query.all()}
                for dept_name, role_name in COMICS_ROLES:
                    dept_id = dept_map.get(dept_name)
                    if dept_id:
                        db.session.add(Role(name=role_name, department_id=dept_id))
                db.session.commit()
