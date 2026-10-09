import json as _json
import os
import uuid
from datetime import date

from flask import Blueprint, current_app, render_template, request, redirect

from app.extensions import db
from app.models.audit import log_contribution
from app.models.comics import (
    CREDIT_TARGET_ISSUE, CREDIT_TARGET_SEGMENT,
    CharacterAppearance, ComicIssue, ComicSeries, ComicSegment, Credit, ExternalLink,
)
from app.models.preferences import UserPreferences
from app.models.reference import (
    Character, CharacterPersona, Creator, CreatorAlias, Department, Era, Imprint, Publisher, Role,
)
from app.utils import make_unique_slug, natural_issue_key

comics_bp = Blueprint('comics', __name__)

# ------------------------------------------------------------------
# Issue form constants
# ------------------------------------------------------------------

ISSUE_DESIGNATIONS = [
    ('regular_issue',     'Regular Issue'),
    ('annual',            'Annual'),
    ('one_shot',          'One-Shot'),
    ('collected_edition', 'Collected Edition'),
    ('graphic_novel',     'Graphic Novel'),
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
    'one_shot':          'comic',
    'collected_edition': 'paperback',
    'graphic_novel':     'hardcover',
}

_COVER_EXTS = {'jpg', 'jpeg', 'png', 'webp', 'gif'}

SERIES_TYPES = [
    ('regular_series', 'Regular Series'),
    ('one_shot',       'One-Shot'),
    ('collection',     'Collection'),
    ('graphic_novel',  'Graphic Novel'),
]


def _get_canon_eras():
    return Era.query.filter_by(continuity='canon').order_by(Era.sort_order).all()


def _get_legends_eras():
    return Era.query.filter_by(continuity='legends').order_by(Era.sort_order).all()


@comics_bp.route('/comics/series/new', methods=['GET', 'POST'])
def series_new():
    prefs = UserPreferences.query.first()
    initial_continuity = prefs.continuity_filter if prefs else 'both'

    if request.method == 'POST':
        return _handle_series_create(initial_continuity)

    return render_template('comics/series_new.html',
                           initial_continuity=initial_continuity,
                           canon_eras=_get_canon_eras(),
                           legends_eras=_get_legends_eras(),
                           series_types=SERIES_TYPES,
                           form={},
                           errors=[])


def _handle_series_create(initial_continuity):
    f = request.form
    errors = []

    title            = f.get('title', '').strip()
    series_type      = f.get('series_type', '').strip()
    continuity       = f.get('continuity', '').strip()
    canon_era_raw    = f.get('canon_era_id', '').strip()
    legends_era_raw  = f.get('legends_era_id', '').strip()
    pub_id_raw       = f.get('publisher_id', '').strip()
    pub_q            = f.get('publisher_q', '').strip()
    imp_id_raw       = f.get('imprint_id', '').strip()
    imp_q            = f.get('imprint_q', '').strip()
    start_year       = f.get('start_year', '').strip() or None
    end_year         = f.get('end_year', '').strip() or None
    synopsis         = f.get('synopsis', '').strip() or None

    valid_types = {v for v, _ in SERIES_TYPES}

    if not title:
        errors.append('Title is required.')
    if series_type not in valid_types:
        errors.append('Series Type is required.')
    if continuity not in ('canon', 'legends', 'both'):
        errors.append('Continuity is required.')
    if continuity in ('canon', 'both') and not canon_era_raw:
        errors.append('Canon Era is required.' if continuity == 'both' else 'Era is required.')
    if continuity in ('legends', 'both') and not legends_era_raw:
        errors.append('Legends Era is required.' if continuity == 'both' else 'Era is required.')
    if not pub_id_raw and not pub_q:
        errors.append('Publisher is required.')

    if errors:
        return render_template('comics/series_new.html',
                               initial_continuity=initial_continuity,
                               canon_eras=_get_canon_eras(),
                               legends_eras=_get_legends_eras(),
                               series_types=SERIES_TYPES,
                               form=f,
                               errors=errors), 422

    # Resolve eras — 'multiple' value sets is_timeline_spanning
    is_timeline_spanning = (canon_era_raw == 'multiple' or legends_era_raw == 'multiple')
    canon_era_id   = None if (not canon_era_raw or canon_era_raw == 'multiple') else int(canon_era_raw)
    legends_era_id = None if (not legends_era_raw or legends_era_raw == 'multiple') else int(legends_era_raw)

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
        canon_era_id=canon_era_id,
        legends_era_id=legends_era_id,
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
                         'canon_era_id': series.canon_era_id,
                         'legends_era_id': series.legends_era_id,
                         'is_timeline_spanning': series.is_timeline_spanning,
                         'publisher_id': series.publisher_id,
                         'imprint_id': series.imprint_id,
                     })
    db.session.commit()

    return redirect(f'/comics/series/{series.id}')


@comics_bp.route('/comics/series/<int:series_id>')
def series_hub(series_id):
    series = ComicSeries.query.get_or_404(series_id)

    # Release date first; natural issue-number order breaks ties (½, 1, 1.AU, 2)
    regular_issues = sorted(
        series.issues.filter_by(designation='regular_issue').all(),
        key=lambda i: (i.release_date, natural_issue_key(i.issue_number)))
    annuals = (series.issues
               .filter_by(designation='annual')
               .order_by(ComicIssue.release_date)
               .all())
    one_shots = (series.issues
                 .filter_by(designation='one_shot')
                 .order_by(ComicIssue.release_date)
                 .all())
    collected = (series.issues
                 .filter_by(designation='collected_edition')
                 .order_by(ComicIssue.release_date)
                 .all())

    return render_template('comics/series_hub.html',
                           series=series,
                           regular_issues=regular_issues,
                           annuals=annuals,
                           one_shots=one_shots,
                           collected=collected)


# ------------------------------------------------------------------
# Issue form
# ------------------------------------------------------------------

def _issue_form_context(series):
    story_depts   = Department.query.filter_by(pillar='comics', scope='story').order_by(Department.id).all()
    product_depts = Department.query.filter_by(pillar='comics', scope='product').order_by(Department.id).all()
    return dict(
        series=series,
        designations=ISSUE_DESIGNATIONS,
        bindings=PHYSICAL_BINDINGS,
        trim_sizes=TRIM_SIZES,
        age_ratings=AGE_RATINGS,
        format_defaults=FORMAT_DEFAULTS,
        allowed_designations={k: sorted(v) for k, v in _TYPE_ALLOWED_DESIGNATIONS.items()},
        blocked_bindings={k: sorted(v) for k, v in _BINDING_BLOCKED.items()},
        story_depts=story_depts,
        product_depts=product_depts,
    )


# Series type → issue types it may hold (PRD §3.2.4). The form reads this same table.
_TYPE_ALLOWED_DESIGNATIONS = {
    'regular_series': {'regular_issue', 'annual', 'one_shot', 'collected_edition'},
    'one_shot':       {'one_shot'},
    'collection':     {'collected_edition'},
    'graphic_novel':  {'graphic_novel'},
}

# Series type → formats it may NOT use. Collections and graphic novels are never "Comic".
_BINDING_BLOCKED = {
    'collection':    {'comic'},
    'graphic_novel': {'comic'},
}


@comics_bp.route('/comics/series/<int:series_id>/issues/new', methods=['GET', 'POST'])
def issue_new(series_id):
    series = ComicSeries.query.get_or_404(series_id)

    # One-Shot series may only ever have one issue
    if series.series_type == 'one_shot' and series.issues.count() >= 1:
        return redirect(f'/comics/series/{series.id}')

    if request.method == 'POST':
        return _handle_issue_create(series)

    return render_template('comics/issue_new.html',
                           form={}, errors=[],
                           **_issue_form_context(series))


def _resolve_creator(creator_id, creator_q):
    if creator_id:
        c = db.session.get(Creator, creator_id)
        if c:
            return c
    if not creator_q:
        return None
    c = Creator.query.filter(db.func.lower(Creator.name) == creator_q.lower()).first()
    if c:
        return c
    c = Creator(name=creator_q, slug=make_unique_slug(creator_q, Creator))
    db.session.add(c)
    db.session.flush()
    log_contribution('create', 'creator', c.id, new_value={'name': c.name, 'slug': c.slug})
    return c


def _resolve_role(role_name, dept_id):
    if not role_name or not dept_id:
        return
    exists = Role.query.filter(
        Role.department_id == dept_id,
        db.func.lower(Role.name) == role_name.lower()
    ).first()
    if not exists:
        max_sort = db.session.query(db.func.max(Role.sort_order)).filter_by(
            department_id=dept_id).scalar() or 0
        db.session.add(Role(name=role_name, department_id=dept_id,
                            sort_order=max_sort + 10))
        db.session.flush()


def _resolve_character(character_id, character_q):
    if character_id:
        c = db.session.get(Character, character_id)
        if c:
            return c
    if not character_q:
        return None
    c = Character.query.filter(
        db.func.lower(Character.baseline_name) == character_q.lower()
    ).first()
    if c:
        return c
    c = Character(baseline_name=character_q,
                  slug=make_unique_slug(character_q, Character),
                  continuity='both')
    db.session.add(c)
    db.session.flush()
    log_contribution('create', 'character', c.id,
                     new_value={'baseline_name': c.baseline_name,
                                'slug': c.slug, 'continuity': c.continuity})
    return c


def _as_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _iter_credit_rows(story_data):
    """Every credit row in a Story Breakdown payload (product and story scope)."""
    yield from story_data.get('issue_credits', [])
    for seg in story_data.get('segments', []):
        yield from seg.get('credits', [])


def _validate_credit_attributes(story_data):
    """Check the "credited as" alias on each credit row before anything is saved.

    An alias must belong to the same person as the credit, and an Uncredited credit
    cannot also say "credited as" a name.
    """
    errors = []
    for row in _iter_credit_rows(story_data):
        if not row.get('alias_id'):
            continue
        alias_id = _as_int(row.get('alias_id'))
        if row.get('is_uncredited'):
            errors.append('A credit cannot be both Uncredited and "credited as" a name.')
            continue
        alias = db.session.get(CreatorAlias, alias_id) if alias_id else None
        creator_id = _as_int(row.get('creator_id'))
        if alias is None or not creator_id or alias.canonical_creator_id != creator_id:
            errors.append('"Credited as" must be one of the credited person\'s saved names.')
    return errors


def _add_credit(data, creator, dept_id, role_name, target_type, target_id, scope):
    """Create one credit (and its log entry) from a Story Breakdown credit row."""
    note = (data.get('note') or '').strip() or None
    credit = Credit(creator_id=creator.id,
                    alias_id=_as_int(data.get('alias_id')),
                    target_type=target_type, target_id=target_id,
                    department_id=dept_id, role_name=role_name, scope=scope,
                    is_uncredited=bool(data.get('is_uncredited', False)),
                    note=note)
    db.session.add(credit)
    db.session.flush()
    log_contribution('create', 'credit', credit.id,
                     new_value={'creator_id': credit.creator_id,
                                'alias_id': credit.alias_id,
                                'target_type': credit.target_type,
                                'target_id': credit.target_id,
                                'department_id': credit.department_id,
                                'role_name': credit.role_name,
                                'scope': credit.scope,
                                'is_uncredited': credit.is_uncredited,
                                'note': credit.note})
    return credit


def _save_story_breakdown(issue, story_data):
    # Issue credits — product scope
    for ic in story_data.get('issue_credits', []):
        dept_id   = ic.get('dept_id')
        role_name = (ic.get('role') or '').strip()
        creator   = _resolve_creator(ic.get('creator_id'), (ic.get('creator_q') or '').strip())
        if not creator or not dept_id:
            continue
        _resolve_role(role_name, dept_id)
        _add_credit(ic, creator, dept_id, role_name,
                    CREDIT_TARGET_ISSUE, issue.id, 'product')

    # Segments
    for seg_data in story_data.get('segments', []):
        segment = ComicSegment(
            issue_id=issue.id,
            sort_order=seg_data.get('sort_order', 1),
            segment_type=seg_data.get('segment_type') or None,
            reproduction='original',
            title=seg_data.get('title') or None,
            colors=seg_data.get('colors') or None,
            pages=seg_data.get('pages') or None,
        )
        db.session.add(segment)
        db.session.flush()
        log_contribution('create', 'comic_segment', segment.id,
                         new_value={'issue_id': segment.issue_id,
                                    'sort_order': segment.sort_order,
                                    'segment_type': segment.segment_type,
                                    'title': segment.title})

        # Story credits — story scope
        for sc in seg_data.get('credits', []):
            dept_id   = sc.get('dept_id')
            role_name = (sc.get('role') or '').strip()
            creator   = _resolve_creator(sc.get('creator_id'), (sc.get('creator_q') or '').strip())
            if not creator or not dept_id:
                continue
            _resolve_role(role_name, dept_id)
            _add_credit(sc, creator, dept_id, role_name,
                        CREDIT_TARGET_SEGMENT, segment.id, 'story')

        # Character appearances
        for cd in seg_data.get('characters', []):
            app_type = (cd.get('appearance_type') or '').strip()
            if app_type not in ('main', 'supporting', 'cameo', 'vision'):
                continue
            character = _resolve_character(cd.get('character_id'),
                                           (cd.get('character_q') or '').strip())
            if not character:
                continue
            persona_id = cd.get('persona_id')
            if persona_id:
                persona = db.session.get(CharacterPersona, persona_id)
                if not persona or persona.baseline_character_id != character.id:
                    persona_id = None
            appearance = CharacterAppearance(
                segment_id=segment.id,
                character_id=character.id,
                persona_id=persona_id,
                appearance_type=app_type,
            )
            db.session.add(appearance)
            db.session.flush()
            log_contribution('create', 'character_appearance', appearance.id,
                             new_value={'segment_id': appearance.segment_id,
                                        'character_id': appearance.character_id,
                                        'persona_id': appearance.persona_id,
                                        'appearance_type': appearance.appearance_type})


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

    typed_text       = f.get('issue_number', '').strip()
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

    # Parse story breakdown
    story_data = None
    story_raw = f.get('story_json', '').strip()
    if story_raw:
        try:
            story_data = _json.loads(story_raw)
        except (ValueError, TypeError):
            errors.append('Story breakdown data was malformed. Please try again.')

    valid_designations = {v for v, _ in ISSUE_DESIGNATIONS}
    valid_bindings     = {v for v, _ in PHYSICAL_BINDINGS}

    # The shared Issue # / Title box: a number for Regular Issues only; for every other
    # type the text is the title and issue_number stays empty (PRD §3.2.4).
    if designation == 'regular_issue':
        issue_number = typed_text.lstrip('#').strip() or None
        issue_title  = None
    else:
        issue_number = None
        issue_title  = typed_text or None

    # Collected Editions and One-Shots may have no subtitle
    optional_text = {'collected_edition', 'one_shot'}
    if designation in valid_designations and not typed_text and designation not in optional_text:
        label = 'Issue #' if designation == 'regular_issue' else (
            'Annual' if designation == 'annual' else 'Title')
        errors.append(f'{label} is required.')
    if issue_number and len(issue_number) > 20:
        errors.append('Issue # is too long (20 characters at most).')
    if issue_title and len(issue_title) > 255:
        errors.append('Title is too long (255 characters at most).')
    if not release_date_s:
        errors.append('Release Date is required.')
    if designation not in valid_designations:
        errors.append('Issue Type is required.')
    if physical_binding not in valid_bindings:
        errors.append('Format is required.')

    # Segment count — strict server-side enforcement
    if not story_data or not story_data.get('segments'):
        errors.append('At least one segment is required.')
    elif isinstance(story_data, dict):
        errors.extend(_validate_credit_attributes(story_data))

    # Validate designation is allowed for this series type
    if designation in valid_designations:
        allowed = _TYPE_ALLOWED_DESIGNATIONS.get(series.series_type)
        if allowed is not None and designation not in allowed:
            errors.append(
                f'Issue Type "{designation.replace("_", " ").title()}" is not '
                f'allowed for {series.series_type.replace("_", " ").title()} series.'
            )

    # Validate format is allowed for this series type
    blocked_bindings = _BINDING_BLOCKED.get(series.series_type, set())
    if physical_binding in blocked_bindings:
        errors.append(
            f'Format "Comic" is not valid for '
            f'{series.series_type.replace("_", " ").title()} series.'
        )

    # One-Shot series: block second issue
    if series.series_type == 'one_shot' and series.issues.count() >= 1:
        errors.append('One-Shot series can only have one issue.')

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
            # month input sends "YYYY-MM" — store as 1st of that month
            if len(cover_date_s) == 7:
                year, month = cover_date_s.split('-')
                cover_date = date(int(year), int(month), 1)
            else:
                cover_date = date.fromisoformat(cover_date_s)
        except (ValueError, TypeError):
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
        issue_title      = issue_title,
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
                         'issue_title':      issue.issue_title,
                         'release_date':     issue.release_date.isoformat(),
                         'designation':      issue.designation,
                         'physical_binding': issue.physical_binding,
                         'cover_image':      issue.cover_image,
                     })

    _save_story_breakdown(issue, story_data)
    db.session.commit()

    return redirect(f'/comics/series/{series.id}')
