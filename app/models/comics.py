from datetime import datetime, timezone
from app.extensions import db


def _now():
    return datetime.now(timezone.utc)


class ComicSeries(db.Model):
    __tablename__ = 'comic_series'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    series_type = db.Column(db.String(30), nullable=False)
    # series_type values: regular_series, limited_series, one_shot,
    #                     annual, collection, graphic_novel
    continuity = db.Column(db.String(10), nullable=False)  # canon/legends/both
    era_id = db.Column(db.Integer, db.ForeignKey('era.id'), nullable=True)
    is_timeline_spanning = db.Column(db.Boolean, nullable=False, default=False)
    publisher_id = db.Column(db.Integer, db.ForeignKey('publisher.id'), nullable=False)
    imprint_id = db.Column(db.Integer, db.ForeignKey('imprint.id'), nullable=True)
    age_rating = db.Column(db.String(10), nullable=True)  # all_ages/t/t_plus/m
    start_year = db.Column(db.Integer, nullable=True)
    end_year = db.Column(db.Integer, nullable=True)
    synopsis = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=_now)
    updated_at = db.Column(db.DateTime, nullable=False, default=_now, onupdate=_now)

    era = db.relationship('Era', backref='comic_series')
    publisher = db.relationship('Publisher', backref='comic_series')
    imprint = db.relationship('Imprint', backref='comic_series')
    issues = db.relationship('ComicIssue', backref='series', lazy='dynamic',
                             order_by='ComicIssue.issue_number')


class ComicIssue(db.Model):
    __tablename__ = 'comic_issue'

    id = db.Column(db.Integer, primary_key=True)
    series_id = db.Column(db.Integer, db.ForeignKey('comic_series.id'), nullable=False)
    issue_number = db.Column(db.String(20), nullable=False)  # handles #0, #½, #1.AU
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
