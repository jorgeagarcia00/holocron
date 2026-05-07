from flask import Blueprint, render_template, request, redirect

from app.extensions import db
from app.models.audit import log_contribution
from app.models.comics import ComicSeries
from app.models.preferences import UserPreferences
from app.models.reference import Era, Imprint, Publisher
from app.utils import make_unique_slug

comics_bp = Blueprint('comics', __name__)

SERIES_TYPES = [
    ('regular_series', 'Regular Series'),
    ('limited_series', 'Limited Series'),
    ('one_shot',       'One-Shot'),
    ('annual',         'Annual'),
    ('collection',     'Collection'),
    ('graphic_novel',  'Graphic Novel'),
]


def _get_eras(continuity):
    if continuity == 'both':
        return Era.query.order_by(Era.continuity, Era.sort_order).all()
    return Era.query.filter_by(continuity=continuity).order_by(Era.sort_order).all()


@comics_bp.route('/comics/series/new', methods=['GET', 'POST'])
def series_new():
    prefs = UserPreferences.query.first()
    initial_continuity = prefs.continuity_filter if prefs else 'both'

    if request.method == 'POST':
        return _handle_series_create(initial_continuity)

    eras = _get_eras(initial_continuity)
    return render_template('comics/series_new.html',
                           initial_continuity=initial_continuity,
                           eras=eras,
                           series_types=SERIES_TYPES,
                           form={},
                           errors=[])


def _handle_series_create(initial_continuity):
    f = request.form
    errors = []

    title        = f.get('title', '').strip()
    series_type  = f.get('series_type', '').strip()
    continuity   = f.get('continuity', '').strip()
    era_id_raw   = f.get('era_id', '').strip()
    pub_id_raw   = f.get('publisher_id', '').strip()
    pub_q        = f.get('publisher_q', '').strip()
    imp_id_raw   = f.get('imprint_id', '').strip()
    imp_q        = f.get('imprint_q', '').strip()
    start_year   = f.get('start_year', '').strip() or None
    end_year     = f.get('end_year', '').strip() or None
    synopsis     = f.get('synopsis', '').strip() or None

    valid_types = {v for v, _ in SERIES_TYPES}

    if not title:
        errors.append('Title is required.')
    if series_type not in valid_types:
        errors.append('Series Type is required.')
    if continuity not in ('canon', 'legends', 'both'):
        errors.append('Continuity is required.')
    if not era_id_raw:
        errors.append('Era is required.')
    if not pub_id_raw and not pub_q:
        errors.append('Publisher is required.')

    if errors:
        eras = _get_eras(continuity or initial_continuity)
        return render_template('comics/series_new.html',
                               initial_continuity=initial_continuity,
                               eras=eras,
                               series_types=SERIES_TYPES,
                               form=f,
                               errors=errors), 422

    # Resolve era
    is_timeline_spanning = era_id_raw == 'multiple'
    era_id = None if is_timeline_spanning else int(era_id_raw)

    # Resolve publisher — create inline if no ID provided
    if pub_id_raw:
        publisher_id = int(pub_id_raw)
    else:
        pub = Publisher(name=pub_q, slug=make_unique_slug(pub_q, Publisher))
        db.session.add(pub)
        db.session.flush()
        log_contribution('create', 'publisher', pub.id,
                         new_value={'name': pub.name, 'slug': pub.slug})
        publisher_id = pub.id

    # Resolve imprint — create inline if typed but no ID
    imprint_id = None
    if imp_id_raw:
        imprint_id = int(imp_id_raw)
    elif imp_q:
        imp = Imprint(name=imp_q,
                      slug=make_unique_slug(imp_q, Imprint),
                      publisher_id=publisher_id)
        db.session.add(imp)
        db.session.flush()
        log_contribution('create', 'imprint', imp.id,
                         new_value={'name': imp.name, 'slug': imp.slug,
                                    'publisher_id': imp.publisher_id})
        imprint_id = imp.id

    series = ComicSeries(
        title=title,
        series_type=series_type,
        continuity=continuity,
        era_id=era_id,
        is_timeline_spanning=is_timeline_spanning,
        publisher_id=publisher_id,
        imprint_id=imprint_id,
        start_year=int(start_year) if start_year else None,
        end_year=int(end_year) if end_year else None,
        synopsis=synopsis,
    )
    db.session.add(series)
    db.session.flush()
    log_contribution('create', 'comic_series', series.id,
                     new_value={
                         'title': series.title,
                         'series_type': series.series_type,
                         'continuity': series.continuity,
                         'era_id': series.era_id,
                         'is_timeline_spanning': series.is_timeline_spanning,
                         'publisher_id': series.publisher_id,
                         'imprint_id': series.imprint_id,
                     })
    db.session.commit()

    return redirect(f'/comics/series/{series.id}')


@comics_bp.route('/comics/series/<int:series_id>')
def series_hub(series_id):
    series = ComicSeries.query.get_or_404(series_id)
    return render_template('comics/series_hub.html', series=series)
