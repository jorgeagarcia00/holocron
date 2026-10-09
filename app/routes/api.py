from flask import Blueprint, request, jsonify, render_template
from rapidfuzz import fuzz, process

from app.extensions import db
from app.models.audit import log_contribution, to_json_safe
from app.models.reference import (
    Creator, Publisher, Imprint,
    Character, CharacterPersona, Era, Role,
)
from app.utils import make_unique_slug

api_bp = Blueprint('api', __name__)


def _fuzzy(q, choices, limit=10, threshold=50):
    return process.extract(q, choices, scorer=fuzz.WRatio, limit=limit, score_cutoff=threshold)


@api_bp.route('/api/search')
def search():
    q = request.args.get('q', '').strip()
    record_type = request.args.get('type', '').strip()

    if not q or not record_type:
        return jsonify([])

    handlers = {
        'creator':            _search_creator,
        'publisher':          _search_publisher,
        'imprint':            _search_imprint,
        'character':          _search_character,
        'character_persona':  _search_character_persona,
        'era':                _search_era,
        'character_combined': _search_character_combined,
    }

    handler = handlers.get(record_type)
    if not handler:
        return jsonify({'error': f'Unknown type: {record_type}'}), 400

    return jsonify(handler(q))


def _search_creator(q):
    rows = Creator.query.all()
    idx = {r.id: r for r in rows}
    hits = _fuzzy(q, {r.id: r.name for r in rows})
    return [{'id': key, 'name': val, 'slug': idx[key].slug}
            for val, score, key in hits]


def _search_publisher(q):
    rows = Publisher.query.all()
    idx = {r.id: r for r in rows}
    hits = _fuzzy(q, {r.id: r.name for r in rows})
    return [{'id': key, 'name': val, 'slug': idx[key].slug}
            for val, score, key in hits]


def _search_imprint(q):
    rows = Imprint.query.all()
    idx = {r.id: r for r in rows}
    hits = _fuzzy(q, {r.id: r.name for r in rows})
    return [{'id': key, 'name': val, 'slug': idx[key].slug,
             'publisher_id': idx[key].publisher_id}
            for val, score, key in hits]


def _search_character(q):
    rows = Character.query.all()
    idx = {r.id: r for r in rows}
    hits = _fuzzy(q, {r.id: r.baseline_name for r in rows})
    return [{'id': key, 'name': val, 'slug': idx[key].slug,
             'continuity': idx[key].continuity}
            for val, score, key in hits]


def _search_character_persona(q):
    rows = CharacterPersona.query.all()
    idx = {r.id: r for r in rows}
    hits = _fuzzy(q, {r.id: r.persona_name for r in rows})
    return [{'id': key, 'name': val, 'slug': idx[key].slug,
             'baseline_character_id': idx[key].baseline_character_id}
            for val, score, key in hits]


def _search_era(q):
    rows = Era.query.all()
    idx = {r.id: r for r in rows}
    hits = _fuzzy(q, {r.id: r.name for r in rows})
    return [{'id': key, 'name': val, 'continuity': idx[key].continuity}
            for val, score, key in hits]


def _search_character_combined(q):
    """Searches both Character baseline names and CharacterPersona names simultaneously.
    Returns results with character_id and persona_id (null for baseline hits).
    Optional ?continuity= param soft-sorts matching continuity to the top."""
    continuity = request.args.get('continuity', '').strip()

    chars = Character.query.all()
    personas = CharacterPersona.query.all()

    char_map = {c.id: c for c in chars}
    persona_map = {p.id: p for p in personas}

    combined = {}
    for c in chars:
        combined[f'c{c.id}'] = c.baseline_name
    for p in personas:
        combined[f'p{p.id}'] = p.persona_name

    q_lower = q.lower()
    hits = _fuzzy(q, combined)

    # Primary sort: starts-with first; secondary: soft continuity match
    starts = [(v, s, k) for v, s, k in hits if combined[k].lower().startswith(q_lower)]
    others = [(v, s, k) for v, s, k in hits if not combined[k].lower().startswith(q_lower)]
    ordered = (starts + others)[:10]

    if continuity:
        def _cont(key):
            if key.startswith('c'):
                return char_map[int(key[1:])].continuity
            return persona_map[int(key[1:])].continuity

        ordered = sorted(ordered, key=lambda t: (
            0 if _cont(t[2]) == continuity else
            1 if _cont(t[2]) == 'both' else 2
        ))

    results = []
    for _val, _score, key in ordered:
        if key.startswith('c'):
            c = char_map[int(key[1:])]
            results.append({
                'display': c.baseline_name,
                'character_id': c.id,
                'persona_id': None,
            })
        else:
            p = persona_map[int(key[1:])]
            c = char_map[p.baseline_character_id]
            results.append({
                'display': f'{c.baseline_name} as {p.persona_name}',
                'character_id': p.baseline_character_id,
                'persona_id': p.id,
            })
    return results


# ---------------------------------------------------------------------------
# Inline creation
# ---------------------------------------------------------------------------

@api_bp.route('/api/create', methods=['POST'])
def create():
    body = request.get_json(silent=True) or {}
    record_type = body.get('type', '').strip()

    handlers = {
        'creator':           _create_creator,
        'publisher':         _create_publisher,
        'imprint':           _create_imprint,
        'character':         _create_character,
        'character_persona': _create_character_persona,
    }

    handler = handlers.get(record_type)
    if not handler:
        return jsonify({'error': f'Unknown type: {record_type}'}), 400

    result, error = handler(body)
    if error:
        return jsonify({'error': error}), 400

    return jsonify(result), 201


def _require(body, *fields):
    missing = [f for f in fields if not body.get(f, '').strip()
               if isinstance(body.get(f), str) or body.get(f) is None]
    return missing


def _commit_new(record, record_type):
    db.session.add(record)
    db.session.flush()
    log_contribution('create', record_type, record.id,
                     new_value={c.name: to_json_safe(getattr(record, c.name))
                                for c in record.__table__.columns})
    db.session.commit()


def _create_creator(body):
    name = (body.get('name') or '').strip()
    if not name:
        return None, 'name is required'
    record = Creator(name=name, slug=make_unique_slug(name, Creator))
    _commit_new(record, 'creator')
    return {'id': record.id, 'name': record.name, 'slug': record.slug}, None


def _create_publisher(body):
    name = (body.get('name') or '').strip()
    if not name:
        return None, 'name is required'
    record = Publisher(name=name, slug=make_unique_slug(name, Publisher))
    _commit_new(record, 'publisher')
    return {'id': record.id, 'name': record.name, 'slug': record.slug}, None


def _create_imprint(body):
    name = (body.get('name') or '').strip()
    publisher_id = body.get('publisher_id')
    if not name:
        return None, 'name is required'
    if not publisher_id:
        return None, 'publisher_id is required'
    if not Publisher.query.get(publisher_id):
        return None, f'publisher {publisher_id} not found'
    record = Imprint(name=name, slug=make_unique_slug(name, Imprint),
                     publisher_id=publisher_id)
    _commit_new(record, 'imprint')
    return {'id': record.id, 'name': record.name, 'slug': record.slug,
            'publisher_id': record.publisher_id}, None


def _create_character(body):
    name = (body.get('name') or '').strip()
    if not name:
        return None, 'name is required'
    continuity = (body.get('continuity') or 'both').strip()
    if continuity not in ('canon', 'legends', 'both'):
        return None, 'continuity must be canon, legends, or both'
    record = Character(baseline_name=name, slug=make_unique_slug(name, Character),
                       continuity=continuity)
    _commit_new(record, 'character')
    return {'id': record.id, 'name': record.baseline_name,
            'slug': record.slug, 'continuity': record.continuity}, None


def _create_character_persona(body):
    name = (body.get('name') or '').strip()
    baseline_character_id = body.get('baseline_character_id')
    if not name:
        return None, 'name is required'
    if not baseline_character_id:
        return None, 'baseline_character_id is required'
    if not Character.query.get(baseline_character_id):
        return None, f'character {baseline_character_id} not found'
    continuity = (body.get('continuity') or 'both').strip()
    if continuity not in ('canon', 'legends', 'both'):
        return None, 'continuity must be canon, legends, or both'
    record = CharacterPersona(
        persona_name=name, slug=make_unique_slug(name, CharacterPersona),
        baseline_character_id=baseline_character_id, continuity=continuity,
    )
    _commit_new(record, 'character_persona')
    return {'id': record.id, 'name': record.persona_name,
            'slug': record.slug,
            'baseline_character_id': record.baseline_character_id}, None


# ---------------------------------------------------------------------------
# htmx autocomplete (returns HTML fragment)
# ---------------------------------------------------------------------------

@api_bp.route('/api/autocomplete')
def autocomplete():
    record_type = request.args.get('type', '')
    widget = request.args.get('widget', record_type)
    # htmx sends the triggering input's value under its own name (e.g. publisher_q)
    q = (request.args.get('q') or request.args.get(f'{widget}_q', '')).strip()

    if not q or not record_type:
        return ''

    handlers = {
        'publisher':         _search_publisher,
        'imprint':           _search_imprint,
        'creator':           _search_creator,
        'character':         _search_character,
        'character_persona': _search_character_persona,
    }
    handler = handlers.get(record_type)
    if not handler:
        return ''

    # Get fuzzy results then re-rank: starts-with first, filter noise with threshold 65
    q_lower = q.lower()
    all_results = handler(q)
    starts = [r for r in all_results if r['name'].lower().startswith(q_lower)]
    others = [r for r in all_results
              if not r['name'].lower().startswith(q_lower)
              and fuzz.WRatio(q, r['name']) >= 65]
    results = (starts + others)[:8]

    return render_template('partials/autocomplete_results.html',
                           results=results,
                           query=q,
                           record_type=record_type,
                           widget=widget)


# ---------------------------------------------------------------------------
# Role vocabulary autocomplete (returns JSON)
# ---------------------------------------------------------------------------

@api_bp.route('/api/roles')
def roles():
    department_id = request.args.get('department_id', type=int)
    q = request.args.get('q', '').strip()

    if not department_id:
        return jsonify([])

    rows = Role.query.filter_by(department_id=department_id).order_by(
        Role.sort_order, Role.name).all()

    if not q:
        return jsonify([r.name for r in rows])

    q_lower = q.lower()
    starts = [r.name for r in rows if r.name.lower().startswith(q_lower)]
    others = [r.name for r in rows
              if not r.name.lower().startswith(q_lower)
              and fuzz.WRatio(q, r.name) >= 60]
    return jsonify((starts + others)[:10])
