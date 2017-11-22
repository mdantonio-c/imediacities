# -*- coding: utf-8 -*-

from restapi.tests import BaseTests
from utilities.htmlcodes import HTTP_OK_BASIC, HTTP_BAD_UNAUTHORIZED
from utilities.logs import get_logger

log = get_logger(__name__)


class TestApp(BaseTests):

    def test_status(self, client):

        res = client.get('/api/stage')
        assert res.status_code == HTTP_BAD_UNAUTHORIZED

        headers, _ = self.do_login(client, None, None)
        res = client.get('/api/stage', headers=headers)

        assert res.status_code == HTTP_OK_BASIC
        # assert res.json == {'ping': 'pong'}
