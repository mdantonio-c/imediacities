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

        #  Prima devo fare una ricerca sui video esistenti per trovare un video
        #    di cui prendere uno shot per avere lo shot_id
        video_id = None
        shot_id = None
        # log in
        log.debug("*** Do login")
        headers, _ = self.do_login(client, None, None)
        res = client.get('/api/videos', headers=headers)
        assert res.status_code == hcodes.HTTP_OK_BASIC
        contents = json.loads(res.data.decode('utf-8'))
        if contents is not None:
            #log.debug("*** Response get videos: "+json.dumps(contents))
            datas = contents.get('Response', {}).get('data', {})
            if datas is not None and datas[0] is not None:
                video_id = datas[0].get("id")
                # deve esistere almeno un video per fare i test
                assert video_id is not None
                #log.debug("*** videos[0] id: " + video_id)
                # GET shots
                res = client.get('/api/videos/' + video_id + '/shots', headers=headers)
                assert res.status_code == hcodes.HTTP_OK_BASIC
                shots_res = json.loads(res.data.decode('utf-8'))
                #log.debug("*** Response of GET video shots: "+json.dumps(shots_res))
                if shots_res is not None:
                    shots_list = shots_res.get('Response', {}).get('data', {})
                    if shots_list is not None:
                        #log.debug("*** number of shots: " + str(len(shots_list)))
                        if shots_list[0] is not None:
                            #log.debug("*** shots[0]: " + json.dumps(shots_list[0]))
                            shot_id = shots_list[0].get("id")
                            # deve esistere lo shot_id
                            assert shot_id is not None
                            #log.debug("*** shot id: " + shot_id)
        if shot_id is not None:
            log.info("*** Testing GET shot by id")
            # GET a shot with a specific id
            # at the moment authorization token not required for GET shot 
            res = client.get('/api/shots/' + shot_id) 
            assert res.status_code == hcodes.HTTP_OK_BASIC
            shot_content = json.loads(res.data.decode('utf-8'))
            #log.debug("*** Response of GET shots with id: "+json.dumps(shot_content))
            if shot_content is not None:
                shot_data = shot_content.get('Response', {}).get('data', {})
                if shot_data is not None:
                    shot_attributes = shot_data.get('attributes')
                    if shot_attributes is not None:
                        shot_number = shot_attributes.get('shot_num')
                        #log.debug("*** shot number: " + str(shot_number))
            log.info("*** Testing GET shot thumbnail")
            # GET shot thumbnail
            res = client.get('/api/shots/' + shot_id + '?content=thumbnail')
            assert res.status_code == hcodes.HTTP_OK_BASIC
            log.debug("*** Got http status " + str(hcodes.HTTP_OK_BASIC))

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