import re
import unicodedata

_FRACTIONS = {'½': 0.5, '⅓': 1 / 3, '⅔': 2 / 3, '¼': 0.25, '¾': 0.75}
_NUMBER_RE = re.compile(r'^\s*(\d+(?:\.\d+)?)?\s*([½⅓⅔¼¾])?\s*(.*)$')


def slugify(text):
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^\w\s-]', '', text.lower())
    return re.sub(r'[-\s]+', '-', text).strip('-')


def make_unique_slug(text, model, slug_field='slug'):
    from app.extensions import db
    base = slugify(text)
    slug = base
    counter = 2
    while db.session.query(model).filter(
        getattr(model, slug_field) == slug
    ).first() is not None:
        slug = f'{base}-{counter}'
        counter += 1
    return slug


def natural_issue_key(issue_number):
    """Sort key for issue numbers: ½ = 0.5, and a suffix such as .AU sorts after the bare number.

    "0" < "½" < "1" < "1.AU" < "2". Non-numeric text sorts last, alphabetically.
    """
    text = (issue_number or '').strip()
    match = _NUMBER_RE.match(text)
    whole, fraction, suffix = match.groups()
    if whole is None and fraction is None:
        return (1, 0.0, text.lower())
    value = float(whole) if whole is not None else 0.0
    if fraction is not None:
        value += _FRACTIONS[fraction]
    return (0, value, suffix.lower())
