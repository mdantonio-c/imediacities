from utilities.logs import get_logger
from restapi.services.authentication import BaseAuthentication as ba
from utilities import htmlcodes as hcodes
from restapi.tests.utilities import AUTH_URI
import json


log = get_logger(__name__)

class TestApp:

    # non e' prevista la possibilita' di fare get con uno specifico group_id

    def test_get(self, client): #client e' una fixture di pytest-flask
        """
            Test GET method of /api/admin/groups
        """
        log.info("*** Testing GET groups")

        # try without log in
        res = client.get('/api/admin/groups')
        # This endpoint requires a valid authorization token
        assert res.status_code == hcodes.HTTP_BAD_UNAUTHORIZED 
        log.debug("*** Got http status " + str(hcodes.HTTP_BAD_UNAUTHORIZED))

        # log in
        log.debug("*** Do login")
        headers, _ = self.do_login(client, None, None)

        # GET groups without a specific id, get all groups
        res = client.get('/api/admin/groups', headers=headers)
        assert res.status_code == hcodes.HTTP_OK_BASIC
        contents = json.loads(res.data.decode('utf-8'))
        log.debug("*** Response of GET groups: "+json.dumps(contents))

        group_id = None

        if contents is not None:
            datas = contents.get('Response', {}).get('data', {})
            if datas is not None and datas[0] is not None:
                # datas e' una lista
                group_id = datas[0].get("id")
                log.debug("*** groups[0] id: " + group_id)


    # TODO post
    #def test_post(self, client):
    #    """
    #        Test POST method of /api/admin/groups
    #    """
    #    log.info("*** Testing POST group")

    # TODO put
    #def test_put(self, client):
    #    """
    #        Test POST method of /api/admin/groups
    #    """
    #    log.info("*** Testing PUT group")
        
    #TODO delete
    #def test_delete(self, client):
    #    """
    #        Test DELETE method of /api/admin/groups
    #    """
    #    log.info("*** Testing DELETE group")

    # TODO test get UserGroup  (???)


##############################################################################

    # do_login is temporarily here, it will be handled in a better way 
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