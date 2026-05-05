from datetime import datetime, timezone
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
