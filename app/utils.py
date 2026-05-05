import re
import unicodedata


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
