from utilities.logs import get_logger
from restapi.services.authentication import BaseAuthentication as ba
from utilities import htmlcodes as hcodes
from restapi.tests.utilities import AUTH_URI
import json


log = get_logger(__name__)

class TestApp:

    def test_get(self, client): #client e' una fixture di pytest-flask
        """
            Test GET method of /api/annotations
        """
        log.info("*** Testing GET annotations")

        # try without log in
        res = client.get('/api/annotations')
        assert res.status_code == hcodes.HTTP_BAD_UNAUTHORIZED # This endpoint requires a valid authorization token
        log.debug("*** Got http status " + str(hcodes.HTTP_BAD_UNAUTHORIZED))

        # log in
        log.debug("*** Do login")
        headers, _ = self.do_login(client, None, None)
        #self.save("auth_header", headers)

        log.debug("*** headers="+json.dumps(headers))

        # GET all annotations of type TVS, with pagination parameters
        res = client.get('/api/annotations?type=VIM&pageSize=10&pageNumber=1', headers=headers)
        assert res.status_code == hcodes.HTTP_OK_BASIC
        content = json.loads(res.data.decode('utf-8'))
        #log.debug("*** Response of GET annotations: "+json.dumps(content))

        anno_id = None

        if content is not None:
            data = content.get('Response', {}).get('data', {})
            if data is not None and data[0] is not None:
                # data e' una lista
                anno_id = data[0].get("id")
                log.debug("*** annotations[0] id: " + anno_id)

        # GET an annotations with a specific id
        if anno_id is not None:
            res = client.get('/api/annotations/'+anno_id, headers=headers)
            assert res.status_code == hcodes.HTTP_OK_BASIC
            content = json.loads(res.data.decode('utf-8'))
            log.debug("*** Response of GET annotations with id: "+json.dumps(content))


    # TODO post
    #def test_post(self, client):
    #    """
    #        Test POST method of /api/annotations
    #    """
    #    log.info("*** Testing POST annotations")
        
    #TODO delete
    #def test_delete(self, client):
    #    """
    #        Test DELETE method of /api/annotations
    #    """
    #    log.info("*** Testing DELETE annotations")


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