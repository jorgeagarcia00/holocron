from datetime import datetime, timezone
from app.extensions import db


def _now():
    return datetime.now(timezone.utc)


class ComicSeries(db.Model):
    __tablename__ = 'comic_series'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    series_type = db.Column(db.String(30), nullable=False)
    # series_type values: regular_series, one_shot, collection, graphic_novel
    continuity = db.Column(db.String(10), nullable=False)  # canon/legends/both
    canon_era_id = db.Column(db.Integer, db.ForeignKey('era.id'), nullable=True)
    legends_era_id = db.Column(db.Integer, db.ForeignKey('era.id'), nullable=True)
    is_timeline_spanning = db.Column(db.Boolean, nullable=False, default=False)
    publisher_id = db.Column(db.Integer, db.ForeignKey('publisher.id'), nullable=False)
    imprint_id = db.Column(db.Integer, db.ForeignKey('imprint.id'), nullable=True)
    age_rating = db.Column(db.String(10), nullable=True)  # all_ages/t/t_plus/m
    volume = db.Column(db.Integer, nullable=True)  # blank = no "Vol. N" tag
    start_year = db.Column(db.Integer, nullable=True)
    end_year = db.Column(db.Integer, nullable=True)
    synopsis = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=_now)
    updated_at = db.Column(db.DateTime, nullable=False, default=_now, onupdate=_now)

    canon_era = db.relationship('Era', foreign_keys=[canon_era_id], backref='canon_comic_series')
    legends_era = db.relationship('Era', foreign_keys=[legends_era_id], backref='legends_comic_series')
    publisher = db.relationship('Publisher', backref='comic_series')
    imprint = db.relationship('Imprint', backref='comic_series')
    issues = db.relationship('ComicIssue', backref='series', lazy='dynamic',
                             order_by='ComicIssue.issue_number')

    @property
    def cover_issue(self):
        """Earliest-release Regular Issue that has a cover (PRD §3.2.3); None if there is none."""
        from app.utils import natural_issue_key
        candidates = self.issues.filter(ComicIssue.designation == 'regular_issue',
                                        ComicIssue.cover_image.isnot(None),
                                        ComicIssue.cover_image != '').all()
        if not candidates:
            return None
        return min(candidates,
                   key=lambda i: (i.release_date, natural_issue_key(i.issue_number)))


class ComicIssue(db.Model):
    __tablename__ = 'comic_issue'

    id = db.Column(db.Integer, primary_key=True)
    series_id = db.Column(db.Integer, db.ForeignKey('comic_series.id'), nullable=False)
    # issue_number is used by regular issues only (stored without "#"; handles 0, ½, 1.AU).
    # Annuals, one-shots, collected editions and graphic novels keep their text in
    # issue_title and leave issue_number empty (PRD §3.2.4).
    issue_number = db.Column(db.String(20), nullable=True)
    issue_title = db.Column(db.String(255), nullable=True)
    release_date = db.Column(db.Date, nullable=False)
    cover_date = db.Column(db.Date, nullable=True)
    # designation = issue type: regular_issue, annual, graphic_novel, collected_edition
    designation = db.Column(db.String(30), nullable=False)
    # physical_binding = format: comic, paperback, hardcover, digital
    physical_binding = db.Column(db.String(20), nullable=False)
    # trim_size: standard, digest, oversized, digital, other
    trim_size = db.Column(db.String(20), nullable=True)
    trim_size_custom = db.Column(db.String(100), nullable=True)  # when trim_size = 'other'
    pages = db.Column(db.Integer, nullable=True)
    age_rating = db.Column(db.String(10), nullable=True)
    price = db.Column(db.Numeric(6, 2), nullable=True)
    upc_isbn = db.Column(db.String(30), nullable=True)
    synopsis = db.Column(db.Text, nullable=True)
    cover_image = db.Column(db.String(255), nullable=True)
    wookieepedia_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=_now)
    updated_at = db.Column(db.DateTime, nullable=False, default=_now, onupdate=_now)

    segments = db.relationship('ComicSegment', backref='issue', lazy='dynamic',
                               order_by='ComicSegment.sort_order')
    external_links = db.relationship('ExternalLink', backref='issue', lazy=True)


class ExternalLink(db.Model):
    __tablename__ = 'external_link'

    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey('comic_issue.id'), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    label = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=_now)


class ComicSegment(db.Model):
    __tablename__ = 'comic_segment'

    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey('comic_issue.id'), nullable=False)
    sort_order = db.Column(db.Integer, nullable=False)
    # segment_type: story, text_story, data_page, illustration, process_art,
    #               script, introduction, afterword, text_article, letters,
    #               cover_gallery, recap
    segment_type = db.Column(db.String(30), nullable=True)
    # reproduction: original, reprint, remaster, altered, compilation, excerpt
    reproduction = db.Column(db.String(20), nullable=True, default='original')
    title = db.Column(db.String(255), nullable=True)
    # colors: color, black_and_white, color_and_black_and_white
    colors = db.Column(db.String(30), nullable=True)
    pages = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=_now)
    updated_at = db.Column(db.DateTime, nullable=False, default=_now, onupdate=_now)

    credits = db.relationship('Credit', backref='segment',
                              primaryjoin='Credit.segment_id == ComicSegment.id',
                              lazy='dynamic')
    appearances = db.relationship('CharacterAppearance', backref='segment', lazy='dynamic')
    # Relationships for segment provenance chain
    derived_from = db.relationship(
        'SegmentRelationship',
        foreign_keys='SegmentRelationship.derived_segment_id',
        backref='derived_segment',
        lazy='dynamic',
    )
    source_of = db.relationship(
        'SegmentRelationship',
        foreign_keys='SegmentRelationship.source_segment_id',
        backref='source_segment',
        lazy='dynamic',
    )


class SegmentRelationship(db.Model):
    __tablename__ = 'segment_relationship'

    id = db.Column(db.Integer, primary_key=True)
    source_segment_id = db.Column(db.Integer, db.ForeignKey('comic_segment.id'), nullable=False)
    derived_segment_id = db.Column(db.Integer, db.ForeignKey('comic_segment.id'), nullable=False)
    # reproduction_type: reprint, remaster, altered, compilation, excerpt
    reproduction_type = db.Column(db.String(20), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=_now)


class Credit(db.Model):
    __tablename__ = 'credit'

    id = db.Column(db.Integer, primary_key=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('creator.id'), nullable=False)
    alias_id = db.Column(db.Integer, db.ForeignKey('creator_alias.id'), nullable=True)
    # Exactly one of segment_id / issue_id is set; the other is NULL.
    # segment_id set  → Story Scope (scope = 'story')
    # issue_id set    → Product Scope (scope = 'product')
    segment_id = db.Column(db.Integer, db.ForeignKey('comic_segment.id'), nullable=True)
    issue_id = db.Column(db.Integer, db.ForeignKey('comic_issue.id'), nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    role_name = db.Column(db.String(100), nullable=False)
    scope = db.Column(db.String(10), nullable=False)  # 'story' or 'product'
    is_uncredited = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=_now)

    creator = db.relationship('Creator', backref='credits')
    alias = db.relationship('CreatorAlias', backref='credits')
    department = db.relationship('Department', backref='credits')
    issue = db.relationship('ComicIssue', backref='credits',
                            foreign_keys=[issue_id])


class CharacterAppearance(db.Model):
    __tablename__ = 'character_appearance'

    id = db.Column(db.Integer, primary_key=True)
    segment_id = db.Column(db.Integer, db.ForeignKey('comic_segment.id'), nullable=False)
    character_id = db.Column(db.Integer, db.ForeignKey('character.id'), nullable=False)
    persona_id = db.Column(db.Integer, db.ForeignKey('character_persona.id'), nullable=True)
    # appearance_type: main, supporting, cameo, vision
    appearance_type = db.Column(db.String(15), nullable=False)
    is_uncredited = db.Column(db.Boolean, nullable=False, default=False)
    archivist_note = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=_now)

    character = db.relationship('Character', backref='appearances')
    persona = db.relationship('CharacterPersona', backref='appearances',
                              foreign_keys=[persona_id])


class SeriesMembership(db.Model):
    """Generic join table for Associative Pillars (Film, Books, Audio, Games).
    entry_type discriminates the pillar so entry_id can reference any future
    pillar table without a hard FK."""
    __tablename__ = 'series_membership'

    id = db.Column(db.Integer, primary_key=True)
    series_id = db.Column(db.Integer, nullable=False)   # FK to pillar-specific series table
    entry_id = db.Column(db.Integer, nullable=False)    # FK to pillar-specific entry table
    entry_type = db.Column(db.String(30), nullable=False)  # e.g. 'film', 'book', 'audio', 'game'
    position = db.Column(db.Integer, nullable=True)
    is_primary = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=_now)
