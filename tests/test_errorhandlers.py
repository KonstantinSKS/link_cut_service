def test_404(client):
    got = client.get('/enexpected')
    assert got.status_code == 404, (
        'При обращении к несуществующей странице возвращайте статуc-код `404`'
    )
    assert (
        'If you entered the URL manually please check your spelling and try again.'  # noqa
        not in got.data.decode('utf-8')
    ), (
        'Добавьте обработку обращения к несуществующим страницам. Вам '
        'пригодится шаблон 404.html'
    )
