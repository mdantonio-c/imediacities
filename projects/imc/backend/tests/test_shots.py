from utilities.logs import get_logger
from restapi.services.authentication import BaseAuthentication as ba
from utilities import htmlcodes as hcodes
from restapi.tests.utilities import AUTH_URI
import json


log = get_logger(__name__)

class TestApp:

    def test_get(self, client): #client e' una fixture di pytest-flask
        """
            Test GET method of /api/shots
        """

        # at the moment authorization token not required

        log.info("*** Testing GET shot by id")
        # GET a shot with a specific id
        shot_id="17daf79d-79e7-4488-895d-53d5df41c9e5"
        res = client.get('/api/shots/' + shot_id) 
        assert res.status_code == hcodes.HTTP_OK_BASIC
        shot_content = json.loads(res.data.decode('utf-8'))
        log.debug("*** Response of GET shots with id: "+json.dumps(shot_content))
        if shot_content is not None:
            shot_data = shot_content.get('Response', {}).get('data', {})
            if shot_data is not None:
                shot_attributes = shot_data.get('attributes')
                if shot_attributes is not None:
                    shot_number = shot_attributes.get('shot_num')
                    log.debug("*** shot number: " + str(shot_number))


        log.info("*** Testing GET shot thumbnail")
        # GET shot thumbnail
        res = client.get('/api/shots/' + shot_id + '?content=thumbnail')
        assert res.status_code == hcodes.HTTP_OK_BASIC
        log.debug("*** Got http status " + str(hcodes.HTTP_OK_BASIC))
