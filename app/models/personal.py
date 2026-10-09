from datetime import date, datetime, timezone
from app.extensions import db

# product_type values name the table a product lives in ('comic_issue' now; later
# 'film', 'book', 'game', 'tv_episode', ...). Like credit.target_type and
# series_membership, this is a polymorphic reference with no FK.
MARKS = ('read', 'own', 'wish')


def _now():
    return datetime.now(timezone.utc)


class ProductMark(db.Model):
    """A Read / Own / Wish mark on a product. Marks are independent: one row per
    product per mark. Marks apply to products only, never to stories (PRD §4.6)."""
    __tablename__ = 'product_mark'
    __table_args__ = (
        db.UniqueConstraint('product_type', 'product_id', 'mark',
                            name='uq_product_mark_product_mark'),
    )

    id = db.Column(db.Integer, primary_key=True)
    product_type = db.Column(db.String(30), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    mark = db.Column(db.String(10), nullable=False)  # read / own / wish
    created_at = db.Column(db.DateTime, nullable=False, default=_now)


class LogEntry(db.Model):
    """One Diary entry: the user read (or watched, played...) a product on a date.
    Not the Contribution Log — that is the audit trail of data edits (PRD §2.9)."""
    __tablename__ = 'log_entry'
    __table_args__ = (
        db.Index('ix_log_entry_product', 'product_type', 'product_id'),
    )

    id = db.Column(db.Integer, primary_key=True)
    product_type = db.Column(db.String(30), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    logged_on = db.Column(db.Date, nullable=False, default=date.today)
    read_before = db.Column(db.Boolean, nullable=False, default=False)  # "I've read this before"
    created_at = db.Column(db.DateTime, nullable=False, default=_now)
