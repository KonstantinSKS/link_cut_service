from string import ascii_letters, digits
from random import choices

from .models import URLMap


def get_unique_short_id():
    while True:
        short_id = ''.join(choices(ascii_letters + digits, k=6))
        if not URLMap.query.filter_by(short=short_id).first():
            return short_id