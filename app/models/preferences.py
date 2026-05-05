from app.extensions import db


class UserPreferences(db.Model):
    __tablename__ = 'user_preferences'

    id = db.Column(db.Integer, primary_key=True)
    continuity_filter = db.Column(db.String(10), nullable=False, default='both')
