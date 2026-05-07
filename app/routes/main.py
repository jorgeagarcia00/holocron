from flask import Blueprint, render_template, request, redirect

from app.extensions import db
from app.models.preferences import UserPreferences

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    from app.models.comics import ComicSeries
    prefs = UserPreferences.query.first()
    cf = prefs.continuity_filter if prefs else 'both'

    q = ComicSeries.query
    if cf == 'canon':
        q = q.filter(ComicSeries.continuity.in_(['canon', 'both']))
    elif cf == 'legends':
        q = q.filter(ComicSeries.continuity.in_(['legends', 'both']))

    recent_series = q.order_by(ComicSeries.created_at.desc()).limit(16).all()
    return render_template('index.html', recent_series=recent_series)


@main_bp.route('/preferences/set', methods=['POST'])
def set_preferences():
    value = request.form.get('continuity_filter', 'both')
    if value not in ('canon', 'legends', 'both'):
        value = 'both'
    prefs = UserPreferences.query.first()
    if prefs:
        prefs.continuity_filter = value
        db.session.commit()
    return redirect(request.referrer or '/')
