from utilities.logs import get_logger
from restapi.services.authentication import BaseAuthentication as ba
from utilities import htmlcodes as hcodes
from restapi.tests.utilities import AUTH_URI
import json


log = get_logger(__name__)

class TestApp:

    def test_POST(self, client): #client e' una fixture di pytest-flask
        """
            Test POST method of /api/search
        """
        log.info("*** Testing POST search")

        # try without log in
        res = client.post('/api/search')
        # This endpoint requires a valid authorization token
        assert res.status_code == hcodes.HTTP_BAD_UNAUTHORIZED 
        log.debug("*** Got http status " + str(hcodes.HTTP_BAD_UNAUTHORIZED))

        # log in
        log.debug("*** Do login")
        headers, _ = self.do_login(client, None, None)

        # search all item of type video with pagination parameters
        post_data = {'type': 'video', 'term': '*'}
        res = client.post('/api/search?perpage=10&currentpage=1', headers=headers, data=json.dumps(post_data))

        assert res.status_code == hcodes.HTTP_OK_BASIC
        response = json.loads(res.data.decode('utf-8'))
        #log.debug("*** Response of search: "+json.dumps(response))

        if response is not None:
            videos_data = response.get('Response', {}).get('data', {})
            if videos_data is not None:
                log.debug("*** Number of videos found: " + str(len(videos_data)))


##############################################################################

    # TOFIX: from version 0.5.6 this method will be in BaseTests class
    def do_login(self, client, USER, PWD, status_code=hcodes.HTTP_OK_BASIC,
                 error=None, **kwargs):
        """
            Make login and return both token and authorization header
        """
        if USER is None or PWD is None:
            ba.myinit()
            if USER is None:
                USER = ba.default_user
            if PWD is None:
                PWD = ba.default_password

        data = {'username': USER, 'password': PWD}
        for v in kwargs:
            data[v] = kwargs[v]
        r = client.post(AUTH_URI + '/login', data=json.dumps(data))

        if r.status_code != hcodes.HTTP_OK_BASIC:
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