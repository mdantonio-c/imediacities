from utilities.logs import get_logger
from restapi.services.authentication import BaseAuthentication as ba
from utilities import htmlcodes as hcodes
from restapi.tests.utilities import AUTH_URI
import json


log = get_logger(__name__)

class TestApp:
    #
    # Al momento il metodo POST (Create a new video description) non
    #  fa nulla, quindi non faccio il test.
    # Non potendo creare una new video description non posso nemmeno
    #  testare la DELETE.
    #
    def test_get(self, client): #client e' una fixture di pytest-flask
        """
            Test GET method of /api/videos
        """
        log.info("*** Testing GET videos")
        # try without log in
        res = client.get('/api/videos')
        # This endpoint requires a valid authorization token
        assert res.status_code == hcodes.HTTP_BAD_UNAUTHORIZED 
        log.debug("*** Got http status " + str(hcodes.HTTP_BAD_UNAUTHORIZED))

        # log in
        log.debug("*** Do login")
        headers, _ = self.do_login(client, None, None)

        # GET videos without a specific id, get all videos
        res = client.get('/api/videos', headers=headers)
        assert res.status_code == hcodes.HTTP_OK_BASIC
        contents = json.loads(res.data.decode('utf-8'))
        #log.debug("*** Response of GET videos: "+json.dumps(contents))

        video_id = None
        if contents is not None:
            datas = contents.get('Response', {}).get('data', {})
            if datas is not None and datas[0] is not None:
                # datas e' una lista
                video_id = datas[0].get("id")
                #log.debug("*** videos[0] id: " + video_id)
        video_content = None
        # GET a video with a specific id
        if video_id is not None:
            res = client.get('/api/videos/' + video_id, headers=headers)
            assert res.status_code == hcodes.HTTP_OK_BASIC
            video_content = json.loads(res.data.decode('utf-8'))
            #log.debug("*** Response of GET videos with id: "+json.dumps(video_content))
            if video_content is not None:
                data = video_content.get('Response', {}).get('data', {})
                if data is not None and data[0] is not None:
                   # data e' una lista
                   video_title = data[0].get("attributes").get("identifying_title")
                   #log.debug("*** video title: " + video_title)
        log.info("*** Testing GET video shots")
        if video_id is not None:
            # try without log in
            res = client.get('/api/videos/' + video_id + '/shots')
            # This endpoint requires a valid authorization token
            assert res.status_code == hcodes.HTTP_BAD_UNAUTHORIZED 
            log.debug("*** Got http status " + str(hcodes.HTTP_BAD_UNAUTHORIZED))
            # GET shots 
            res = client.get('/api/videos/' + video_id + '/shots', headers=headers)
            assert res.status_code == hcodes.HTTP_OK_BASIC
            shots_res = json.loads(res.data.decode('utf-8'))
            #log.debug("*** Response of GET video shots: "+json.dumps(shots_res))
            if shots_res is not None:
                shots_list = shots_res.get('Response', {}).get('data', {})
                if shots_list is not None:
                    log.debug("*** number of shots: " + str(len(shots_list)))
                    if shots_list[0] is not None:
                        log.debug("*** shots[0]: " + json.dumps(shots_list[0]))

        log.info("*** Testing GET video annotations")
        if video_id is not None:
            # try without log in
            res = client.get('/api/videos/' + video_id + '/annotations')
            assert res.status_code == hcodes.HTTP_BAD_UNAUTHORIZED # This endpoint requires a valid authorization token
            log.debug("*** Got http status " + str(hcodes.HTTP_BAD_UNAUTHORIZED))
            # GET annotations 
            res = client.get('/api/videos/' + video_id + '/annotations', headers=headers)
            assert res.status_code == hcodes.HTTP_OK_BASIC
            anno_res = json.loads(res.data.decode('utf-8'))
            log.debug("*** Response of GET video annotations: "+json.dumps(anno_res))
            if anno_res is not None:
                anno_list = anno_res.get('Response', {}).get('data', {})
                if anno_list is not None:
                    log.debug("*** number of annotations: " + str(len(anno_list)))
                    if anno_list[0] is not None:
                        log.debug("*** annotations[0]: " + json.dumps(anno_list[0]))

        log.info("*** Testing GET video content")
        if video_id is not None:
            # GET content thumbnail
            # at the moment authorization token not required
            res = client.get('/api/videos/' + video_id + '/content?type=thumbnail')
            assert res.status_code == hcodes.HTTP_OK_BASIC
            #log.debug("*** Got http status " + str(hcodes.HTTP_OK_BASIC))

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