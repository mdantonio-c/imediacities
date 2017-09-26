# import pytest
# from flask import url_for

from utilities.logs import get_logger
log = get_logger(__name__)


class TestApp:

    def test_status(self, client):

        res = client.get('/auth/login')
        assert res.status_code == 200
        assert res.json == {'ping': 'pong'}
