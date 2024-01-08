import pytest

from yacut.models import URLMap

py_url = 'https://www.python.org'


def test_create_id(client):
    got = client.post('/api/id/', json={
        'url': py_url,
        'custom_id': 'py',
    })
    assert got.status_code == 201, (
        'При создании короткой ссылки должен возвращаться статус-код 201'
    )
    assert list(got.json.keys()) == ['short_link', 'url'], (
        'При создании короткой ссылки в ответе должны быть ключи `url, '
        'short_link`'
    )
    assert got.json == {
        'url': py_url,
        'short_link': 'http://localhost/py',
    }, 'При создании короткой ссылки тело ответа API отличается от ожидаемого.'


def test_create_empty_body(client):
    try:
        got = client.post('/api/id/')
    except Exception:
        raise AssertionError(
            'Если в теле запроса не передана информация - вызовите исключение.'
        )
    assert got.status_code == 400, (
        'В ответ на пустой POST-запрос к эндпоинту `/api/id/` должен '
        'вернуться статус-код 400.'
    )
    assert list(got.json.keys()) == ['message'], (
        'В ответе на пустой POST-запрос к эндпоинту `/api/id/` должен быть '
        'ключ `message`'
    )
    assert got.json == {'message': 'Отсутствует тело запроса'}, (
        'Сообщение в теле ответа при создании короткой ссылки '
        'без тела в запросе не соответствует спецификации'
    )


@pytest.mark.parametrize('json_data', [
    ({'url': py_url, 'custom_id': '.,/!?'}),
    ({'url': py_url, 'custom_id': 'Hodor-Hodor'}),
    ({'url': py_url, 'custom_id': 'h@k$r'}),
    ({'url': py_url, 'custom_id': '$'}),
    ({'url': py_url, 'custom_id': 'п'}),
    ({'url': py_url, 'custom_id': 'l l'}),
])
def test_invalid_short_url(json_data, client):
    got = client.post('/api/id/', json=json_data)
    assert got.status_code == 400, (
        'При недопустимом имени для короткой ссылки статус ответа должен '
        'быть 400'
    )
    assert list(got.json.keys()) == ['message'], (
        'При недопустимом имени для короткой ссылки в ответе должен быть '
        'ключ `message`'
    )
    assert (
        got.json == {'message': 'Указано недопустимое имя для короткой ссылки'}
    ), (
        'При недопустимом имени короткой ссылки возвращается сообщение, '
        'не соответствующее спецификации.'
    )
    unique_id = URLMap.query.filter_by(original=py_url).first()
    assert not unique_id, (
        'В короткой ссылке должно быть разрешено использование строго '
        'определённого набора символов. Обратитесь к тексту задания.'
    )


def test_no_required_field(client):
    try:
        got = client.post('/api/id/', json={
            'short_link': 'python',
        })
    except Exception:
        raise AssertionError(
            'Если тело запроса к эндпоинту `/api/id/` отличается от '
            'ожидаемого - выбрасывайте исключение.'
        )
    assert got.status_code == 400, (
        'Если тело запроса к эндпоинту `/api/id/` отличается от ожидаемого '
        '- верните статус-код 400.'
    )
    assert list(got.json.keys()) == ['message'], (
        'Если тело запроса к эндпоинту `/api/id/` отличается от ожидаемого - '
        'верните ответ с ключом `message`.'
    )
    assert got.json == {'message': '\"url\" является обязательным полем!'}, (
        'Сообщение в теле ответа при некорректном теле запроса '
        'не соответствует спецификации'
    )


def test_url_already_exists(client, short_python_url):
    try:
        got = client.post('/api/id/', json={
            'url': py_url,
            'custom_id': 'py',
        })
    except Exception:
        raise AssertionError(
            'При попытке создания ссылки с коротким именем, которое уже '
            'занято - вызывайте исключение.'
        )
    assert got.status_code == 400, (
        'При попытке создания ссылки с коротким именем, которое уже занято - '
        'верните статус-код 400'
    )
    assert list(got.json.keys()) == ['message'], (
        'При попытке создания ссылки с коротким именем, которое уже занято - '
        'верните ответ с ключом `message`.'
    )
    assert (
        got.json == {
            'message': 'Предложенный вариант короткой ссылки уже существует.'
        }
    ), (
        'При попытке создания ссылки с коротким именем, которое уже занято '
        'возвращается сообщение с текстом, не соответствующим спецификации.'
    )


@pytest.mark.parametrize('json_data', [
    ({'url': py_url, 'custom_id': None}),
    ({'url': py_url, 'custom_id': ''}),
])
def test_generated_unique_short_id(json_data, client):
    try:
        got = client.post('/api/id/', json=json_data)
    except Exception:
        raise AssertionError(
            'Для запроса, в котором short_id отсутствует или содержит пустую '
            'строку - генерируйте уникальный short_id.'
        )
    assert got.status_code == 201, (
        'При создании короткой ссылки без явно указанного имени '
        'должен возвращаться статус-код 201'
    )
    unique_id = URLMap.query.filter_by(original=py_url).first()
    assert unique_id, (
        'При создании короткой ссылки без явно указанного имени '
        'нужно сгенерировать относительную часть ссылки '
        'из цифр и символов латиницы - и сохранить ссылку в базе данных'
    )
    assert got.json == {
        'url': py_url,
        'short_link': 'http://localhost/' + unique_id.short,
    }, (
        'При создании короткой ссылки без явно указанного имени '
        'нужно сгенерировать относительную часть ссылки '
        'из цифр и символов латиницы - и вернуть ссылку в ответе API.'
    )


def test_get_url_endpoint(client, short_python_url):
    got = client.get(f'/api/id/{short_python_url.short}/')
    assert got.status_code == 200, (
        'В ответе на GET-запрос к эндпоинту `/api/id/<short_id>/` должен '
        'вернуться статус-код 200'
    )
    assert list(got.json.keys()) == ['url'], (
        'В ответе на GET-запрос к эндпоинту `/api/id/<short_id>/` должен быть '
        'передан ключ `url`'
    )
    assert got.json == {'url': py_url}, (
        'При GET-запросе к эндпоинту `/api/id/<short_id>/` возвращается '
        'ответ, не соответствующий спецификации.'
    )


def test_get_url_not_found(client):
    got = client.get('/api/id/{enexpected}/')
    assert got.status_code == 404, (
        'В ответ на GET-запрос для получения несуществующей ссылки '
        'должен вернуться статус-код 404.'
    )
    assert list(got.json.keys()) == ['message'], (
        'В ответе на GET-запрос для получения несуществующей ссылки должен '
        'быть передан ключ `message`'
    )
    assert got.json == {'message': 'Указанный id не найден'}, (
        'Ответ На GET-запрос для получения несуществующей ссылки не '
        'соответствует спецификации.'
    )


def test_len_short_id_api(client):
    long_string = (
        'CuriosityisnotasinHarryHoweverfromtimetotimeyoushouldexercisecaution'
    )
    got = client.post('/api/id/', json={
        'url': py_url,
        'custom_id': long_string,
    })
    assert got.status_code == 400, (
        'Если при POST-запросе к эндпоинту `/api/id/` '
        'поле `short_id` содержит строку длиннее 16 символов - нужно вернуть '
        'статус-код 400.'
    )
    assert list(got.json.keys()) == ['message'], (
        'Если при POST-запросе к эндпоинту `/api/id/` '
        'поле `short_id` содержит строку длиннее 16 символов - в ответе '
        'должен быть ключ `message`.'
    )
    assert (
        got.json == {'message': 'Указано недопустимое имя для короткой ссылки'}
    ), (
        'При POST-запросе к эндпоинту `/api/id/`, в поле `short_id` которого '
        'передана строка длиннее 16 символов, возвращается ответ, не '
        'соответствующий спецификации.'
    )


def test_len_short_id_autogenerated_api(client):
    client.post('/api/id/', json={
        'url': py_url,
    })
    unique_id = URLMap.query.filter_by(original=py_url).first()
    assert len(unique_id.short) == 6, (
        'При POST-запросе, в теле которого не указана короткая ссылка, '
        'должна генерироваться короткая ссылка длинной 6 символов.'
    )
