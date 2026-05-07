from flask import Blueprint, render_template, request, redirect

from app.extensions import db
from app.models.preferences import UserPreferences

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    return render_template('index.html')


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
