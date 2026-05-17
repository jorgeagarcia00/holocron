from datetime import datetime, timezone
from app.extensions import db


def _now():
    return datetime.now(timezone.utc)


class Era(db.Model):
    __tablename__ = 'era'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    continuity = db.Column(db.String(10), nullable=False)  # 'canon', 'legends'
    in_universe_date_start = db.Column(db.String(50), nullable=True)
    in_universe_date_end = db.Column(db.String(50), nullable=True)
    sort_order = db.Column(db.Integer, nullable=True)


class Publisher(db.Model):
    __tablename__ = 'publisher'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, nullable=False, default=_now)
    updated_at = db.Column(db.DateTime, nullable=False, default=_now, onupdate=_now)

    imprints = db.relationship('Imprint', backref='publisher', lazy=True)


class Imprint(db.Model):
    __tablename__ = 'imprint'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), nullable=False, unique=True)
    publisher_id = db.Column(db.Integer, db.ForeignKey('publisher.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=_now)
    updated_at = db.Column(db.DateTime, nullable=False, default=_now, onupdate=_now)


class Creator(db.Model):
    __tablename__ = 'creator'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), nullable=False, unique=True)
    bio = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=_now)
    updated_at = db.Column(db.DateTime, nullable=False, default=_now, onupdate=_now)

    aliases = db.relationship('CreatorAlias', backref='canonical_creator', lazy=True)


class CreatorAlias(db.Model):
    __tablename__ = 'creator_alias'

    id = db.Column(db.Integer, primary_key=True)
    alias_name = db.Column(db.String(100), nullable=False)
    canonical_creator_id = db.Column(db.Integer, db.ForeignKey('creator.id'), nullable=False)
    alias_type = db.Column(db.String(20), nullable=False)  # 'pseudonym', 'studio', 'name_variation'
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=_now)


class Character(db.Model):
    __tablename__ = 'character'

    id = db.Column(db.Integer, primary_key=True)
    baseline_name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), nullable=False, unique=True)
    continuity = db.Column(db.String(10), nullable=False)  # 'canon', 'legends', 'both'
    bio = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=_now)
    updated_at = db.Column(db.DateTime, nullable=False, default=_now, onupdate=_now)

    personas = db.relationship('CharacterPersona', backref='baseline_character', lazy=True)


class CharacterPersona(db.Model):
    __tablename__ = 'character_persona'

    id = db.Column(db.Integer, primary_key=True)
    persona_name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), nullable=False, unique=True)
    baseline_character_id = db.Column(db.Integer, db.ForeignKey('character.id'), nullable=False)
    continuity = db.Column(db.String(10), nullable=False)  # 'canon', 'legends', 'both'
    first_appearance_segment_id = db.Column(db.Integer, db.ForeignKey('comic_segment.id'), nullable=True)
    image = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=_now)


class Department(db.Model):
    __tablename__ = 'department'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    pillar = db.Column(db.String(20), nullable=False)
    scope = db.Column(db.String(10), nullable=False)  # 'story', 'product'
    created_at = db.Column(db.DateTime, nullable=False, default=_now)


class Role(db.Model):
    __tablename__ = 'role'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    sort_order = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=_now)

    department = db.relationship('Department', backref='roles')
