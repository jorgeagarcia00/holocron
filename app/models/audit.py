from datetime import date, datetime, timezone
from decimal import Decimal
from app.extensions import db


class ContributionLog(db.Model):
    __tablename__ = 'contribution_log'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    action_type = db.Column(db.String(10), nullable=False)   # 'create', 'edit', 'delete'
    record_type = db.Column(db.String(50), nullable=False)
    record_id = db.Column(db.Integer, nullable=False)
    old_value = db.Column(db.JSON, nullable=True)
    new_value = db.Column(db.JSON, nullable=True)
    archivist_note = db.Column(db.Text, nullable=True)


def log_contribution(action_type, record_type, record_id,
                     old_value=None, new_value=None, archivist_note=None):
    entry = ContributionLog(
        action_type=action_type,
        record_type=record_type,
        record_id=record_id,
        old_value=old_value,
        new_value=new_value,
        archivist_note=archivist_note,
    )
    db.session.add(entry)


def log_edit(record_type, record_id, before, after, archivist_note=None):
    """Log an edit as the changed fields only: old_value holds each changed field's value
    before, new_value its value after (PRD §2.9). Returns the entry, or None when nothing
    changed and no note was given. Like log_contribution, the caller commits.

    `before` and `after` are dicts of field name -> value for the same record.
    """
    changed = [k for k in after if before.get(k) != after[k]]
    if not changed and not archivist_note:
        return None
    entry = ContributionLog(
        action_type='edit',
        record_type=record_type,
        record_id=record_id,
        old_value={k: to_json_safe(before.get(k)) for k in changed},
        new_value={k: to_json_safe(after[k]) for k in changed},
        archivist_note=archivist_note or None,
    )
    db.session.add(entry)
    return entry


def to_json_safe(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    return value
