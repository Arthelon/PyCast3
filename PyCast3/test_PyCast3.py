import pytest, requests, json
from .PyCast3 import get_data


def test_get_data():
    with pytest.raises(requests.exceptions.ConnectionError):
        get_data('https://foo.bar')
    with pytest.raises(SystemExit):
        get_data('http://www.google.com/barfoo')
    assert isinstance(get_data('http://jsonip.com/'), dict)
    assert isinstance(get_data('https://google.com', json=False), bytes)
    with pytest.raises(json.decoder.JSONDecodeError):
        get_data('http://www.feedforall.com/sample.xml')


