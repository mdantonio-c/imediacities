# -*- coding: utf-8 -*-

# TOFIX: from version 0.5.6 use BaseTests class
# from restapi.tests import BaseTests
from utilities.htmlcodes import HTTP_OK_BASIC, HTTP_BAD_UNAUTHORIZED
from utilities.logs import get_logger

log = get_logger(__name__)


# TOFIX: from version 0.5.6 inherit from BaseTests class
# class TestApp(BaseTests):
class TestApp:

    def test_status(self, client):

        res = client.get('/api/stage')
        assert res.status_code == HTTP_BAD_UNAUTHORIZED

        headers, _ = self.do_login(client, None, None)
        res = client.get('/api/stage', headers=headers)

        assert res.status_code == HTTP_OK_BASIC
        # assert res.json == {'ping': 'pong'}

    # TOFIX: from version 0.5.6 this method will be in BaseTests class
    def do_login(self, client, USER, PWD, status_code=HTTP_OK_BASIC,
                 error=None, **kwargs):
        """
            Make login and return both token and authorization header
        """
        from restapi.services.authentication import BaseAuthentication as ba
        if USER is None or PWD is None:
            ba.myinit()
            if USER is None:
                USER = ba.default_user
            if PWD is None:
                PWD = ba.default_password

        data = {'username': USER, 'password': PWD}
        for v in kwargs:
            data[v] = kwargs[v]
        import json
        from restapi.tests.utilities import AUTH_URI
        r = client.post(AUTH_URI + '/login', data=json.dumps(data))

        if r.status_code != HTTP_OK_BASIC:
            # VERY IMPORTANT FOR DEBUGGING WHEN ADVANCED AUTH OPTIONS ARE ON
            c = json.loads(r.data.decode('utf-8'))
            log.error(c['Response']['errors'])

        assert r.status_code == status_code

        content = json.loads(r.data.decode('utf-8'))
        if error is not None:
            errors = content['Response']['errors']
            if errors is not None:
                assert errors[0] == error

        token = ''
        if content is not None:
            data = content.get('Response', {}).get('data', {})
            if data is not None:
                token = data.get('token', '')
        return {'Authorization': 'Bearer ' + token}, token
