from sqlalchemy import inspect as sa_inspect
from app.extensions import db


CANON_ERAS = [
    'The Dawn of the Jedi',
    'The Age of the Republic — High Republic Era',
    'The Age of the Republic — Fall of the Jedi',
    'The Age of the Rebellion — Reign of the Empire',
    'The Age of the Rebellion — Age of Rebellion',
    'The New Republic Era',
    'The Rise of the First Order',
    'The New Jedi Order',
    'Multiple Eras',
    'Unknown',
]

COMICS_DEPARTMENTS = [
    ('Writers',   'comics', 'story'),
    ('Artists',   'comics', 'story'),
    ('Editors',   'comics', 'story'),
    ('Cover',     'comics', 'product'),
    ('Production','comics', 'product'),
    ('Lucasfilm', 'comics', 'product'),
]


def _tables_exist(engine, *names):
    existing = sa_inspect(engine).get_table_names()
    return all(n in existing for n in names)


def seed_all(flask_app):
    from app.models.preferences import UserPreferences
    from app.models.reference import Era, Department

    with flask_app.app_context():
        engine = db.engine

        if _tables_exist(engine, 'user_preferences'):
            if not UserPreferences.query.first():
                db.session.add(UserPreferences(continuity_filter='both'))
                db.session.commit()

        if _tables_exist(engine, 'era'):
            if Era.query.count() == 0:
                for name in CANON_ERAS:
                    db.session.add(Era(name=name, continuity='canon'))
                db.session.commit()

        if _tables_exist(engine, 'department'):
            if Department.query.count() == 0:
                for name, pillar, scope in COMICS_DEPARTMENTS:
                    db.session.add(Department(name=name, pillar=pillar, scope=scope))
                db.session.commit()
