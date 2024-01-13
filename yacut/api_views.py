from http import HTTPStatus
from re import match

from flask import jsonify, request

from . import app, db
from .error_handlers import InvalidAPIUsage
from .models import URLMap
from .utils import get_unique_short_id

CUSTOM_ID_MAX_LENGTH = 16


@app.route('/api/id/', methods=['POST'])
def create_short_api():
    data = request.get_json()
    if not data:
        raise InvalidAPIUsage('Отсутствует тело запроса')
    if 'url' not in data:
        raise InvalidAPIUsage('\"url\" является обязательным полем!')
    if not data.get('custom_id'):
        data['custom_id'] = get_unique_short_id()
    elif URLMap.query.filter_by(short=data['custom_id']).first() is not None:
        raise InvalidAPIUsage('Предложенный вариант короткой ссылки уже существует.')
    elif not match(r'^[A-Za-z0-9_]+$', data['custom_id']):
        raise InvalidAPIUsage('Указано недопустимое имя для короткой ссылки')
    elif len(data['custom_id']) > CUSTOM_ID_MAX_LENGTH:
        raise InvalidAPIUsage(
            'Указано недопустимое имя для короткой ссылки')
    url_map = URLMap()
    url_map.from_dict(data)
    db.session.add(url_map)
    db.session.commit()
    return jsonify(url_map.to_dict()), HTTPStatus.CREATED


@app.route('/api/id/<short_id>/', methods=['GET'])
def get_original_url(short_id):
    url = URLMap.query.filter_by(short=short_id).first()
    if url is not None:
        return jsonify({'url': url.original}), HTTPStatus.OK
    raise InvalidAPIUsage('Указанный id не найден', HTTPStatus.NOT_FOUND)