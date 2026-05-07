import os
import uuid
from datetime import date

from flask import Blueprint, current_app, render_template, request, redirect

from app.extensions import db
from app.models.audit import log_contribution
from app.models.comics import ComicIssue, ComicSeries, ExternalLink
from app.models.preferences import UserPreferences
from app.models.reference import Era, Imprint, Publisher
from app.utils import make_unique_slug

comics_bp = Blueprint('comics', __name__)

# ------------------------------------------------------------------
# Issue form constants
# ------------------------------------------------------------------

ISSUE_DESIGNATIONS = [
    ('regular_issue',     'Regular Issue'),
    ('annual',            'Annual'),
    ('graphic_novel',     'Graphic Novel'),
    ('collected_edition', 'Collected Edition'),
]

PHYSICAL_BINDINGS = [
    ('comic',     'Comic'),
    ('paperback', 'Paperback'),
    ('hardcover', 'Hardcover'),
    ('digital',   'Digital'),
]

TRIM_SIZES = [
    ('',          'Select…'),
    ('standard',  'Standard'),
    ('digest',    'Digest'),
    ('oversized', 'Oversized'),
    ('digital',   'Digital'),
    ('other',     'Other…'),
]

AGE_RATINGS = [
    ('',         '—'),
    ('all_ages', 'All Ages'),
    ('t',        'T'),
    ('t_plus',   'T+'),
    ('m',        'M'),
]

# Type → default Format per PRD §3.2.4
FORMAT_DEFAULTS = {
    'regular_issue':     'comic',
    'annual':            'comic',
    'graphic_novel':     'hardcover',
    'collected_edition': 'paperback',
}

_COVER_EXTS = {'jpg', 'jpeg', 'png', 'webp', 'gif'}

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

    # Resolve publisher — use existing if found, else create
    if pub_id_raw:
        publisher_id = int(pub_id_raw)
    else:
        existing_pub = Publisher.query.filter(
            db.func.lower(Publisher.name) == pub_q.lower()
        ).first()
        if existing_pub:
            publisher_id = existing_pub.id
        else:
            pub = Publisher(name=pub_q, slug=make_unique_slug(pub_q, Publisher))
            db.session.add(pub)
            db.session.flush()
            log_contribution('create', 'publisher', pub.id,
                             new_value={'name': pub.name, 'slug': pub.slug})
            publisher_id = pub.id

    # Resolve imprint — use existing if found, else create
    imprint_id = None
    if imp_id_raw:
        imprint_id = int(imp_id_raw)
    elif imp_q:
        existing_imp = Imprint.query.filter(
            db.func.lower(Imprint.name) == imp_q.lower()
        ).first()
        if existing_imp:
            imprint_id = existing_imp.id
        else:
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


# ------------------------------------------------------------------
# Issue form
# ------------------------------------------------------------------

def _issue_form_context(series):
    return dict(
        series=series,
        designations=ISSUE_DESIGNATIONS,
        bindings=PHYSICAL_BINDINGS,
        trim_sizes=TRIM_SIZES,
        age_ratings=AGE_RATINGS,
        format_defaults=FORMAT_DEFAULTS,
    )


@comics_bp.route('/comics/series/<int:series_id>/issues/new', methods=['GET', 'POST'])
def issue_new(series_id):
    series = ComicSeries.query.get_or_404(series_id)

    if request.method == 'POST':
        return _handle_issue_create(series)

    return render_template('comics/issue_new.html',
                           form={}, errors=[],
                           **_issue_form_context(series))


def _save_cover(file):
    ext = file.filename.rsplit('.', 1)[-1].lower()
    filename = uuid.uuid4().hex + '.' + ext
    upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'covers')
    os.makedirs(upload_dir, exist_ok=True)
    file.save(os.path.join(upload_dir, filename))
    return f'uploads/covers/{filename}'


def _handle_issue_create(series):
    f = request.form
    errors = []

    issue_number     = f.get('issue_number', '').strip().lstrip('#')
    release_date_s   = f.get('release_date', '').strip()
    cover_date_s     = f.get('cover_date', '').strip()
    designation      = f.get('designation', '').strip()
    physical_binding = f.get('physical_binding', '').strip()
    trim_size        = f.get('trim_size', '').strip() or None
    trim_size_custom = f.get('trim_size_custom', '').strip() or None
    synopsis_raw     = f.get('synopsis', '').strip()
    synopsis         = None if synopsis_raw in ('', '<p><br></p>') else synopsis_raw
    pages            = f.get('pages', '').strip() or None
    age_rating       = f.get('age_rating', '').strip() or None
    price            = f.get('price', '').strip() or None
    upc_isbn         = f.get('upc_isbn', '').strip() or None
    wookieepedia_url = f.get('wookieepedia_url', '').strip() or None

    valid_designations = {v for v, _ in ISSUE_DESIGNATIONS}
    valid_bindings     = {v for v, _ in PHYSICAL_BINDINGS}

    if not issue_number:
        errors.append('Issue # is required.')
    if not release_date_s:
        errors.append('Release Date is required.')
    if designation not in valid_designations:
        errors.append('Issue Type is required.')
    if physical_binding not in valid_bindings:
        errors.append('Format is required.')

    # Parse dates early so we can report errors
    release_date = None
    if release_date_s:
        try:
            release_date = date.fromisoformat(release_date_s)
        except ValueError:
            errors.append('Release Date is not a valid date.')

    cover_date = None
    if cover_date_s:
        try:
            cover_date = date.fromisoformat(cover_date_s)
        except ValueError:
            pass  # silently ignore bad cover date

    if errors:
        return render_template('comics/issue_new.html',
                               form=f, errors=errors,
                               **_issue_form_context(series)), 422

    # Cover image
    cover_image = None
    cover_file = request.files.get('cover_image')
    if cover_file and cover_file.filename:
        ext = cover_file.filename.rsplit('.', 1)[-1].lower()
        if ext in _COVER_EXTS:
            cover_image = _save_cover(cover_file)

    issue = ComicIssue(
        series_id        = series.id,
        issue_number     = issue_number,
        release_date     = release_date,
        cover_date       = cover_date,
        designation      = designation,
        physical_binding = physical_binding,
        trim_size        = trim_size,
        trim_size_custom = trim_size_custom if trim_size == 'other' else None,
        synopsis         = synopsis,
        pages            = int(pages) if pages else None,
        age_rating       = age_rating,
        price            = float(price) if price else None,
        upc_isbn         = upc_isbn,
        wookieepedia_url = wookieepedia_url,
        cover_image      = cover_image,
    )
    db.session.add(issue)
    db.session.flush()

    # Additional external links
    for url, label in zip(f.getlist('link_url'), f.getlist('link_label')):
        url = url.strip()
        if url:
            db.session.add(ExternalLink(
                issue_id=issue.id,
                url=url,
                label=label.strip() or url,
            ))

    log_contribution('create', 'comic_issue', issue.id,
                     new_value={
                         'series_id':        issue.series_id,
                         'issue_number':     issue.issue_number,
                         'release_date':     issue.release_date.isoformat(),
                         'designation':      issue.designation,
                         'physical_binding': issue.physical_binding,
                         'cover_image':      issue.cover_image,
                     })
    db.session.commit()

    return redirect(f'/comics/series/{series.id}')
