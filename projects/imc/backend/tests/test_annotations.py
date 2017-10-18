from utilities.logs import get_logger
from restapi.services.authentication import BaseAuthentication as ba
from utilities import htmlcodes as hcodes
from restapi.tests.utilities import AUTH_URI
import json


log = get_logger(__name__)

class TestApp:

    def test_annotations(self, client): #client e' una fixture di pytest-flask
        """
            Test the API /api/annotations
        """
        log.info("*** Testing GET annotations")
        # try without log in
        res = client.get('/api/annotations')
        # This endpoint requires a valid authorization token
        assert res.status_code == hcodes.HTTP_BAD_UNAUTHORIZED 
        log.debug("*** Got http status " + str(hcodes.HTTP_BAD_UNAUTHORIZED))
        # log in
        log.debug("*** Do login")
        headers, _ = self.do_login(client, None, None)
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
                #log.debug("*** annotations[0] id: " + anno_id)
        # GET an annotations with a specific id
        if anno_id is not None:
            res = client.get('/api/annotations/'+anno_id, headers=headers)
            assert res.status_code == hcodes.HTTP_OK_BASIC
            content = json.loads(res.data.decode('utf-8'))
            #log.debug("*** Response of GET annotations with id: "+json.dumps(content))

        # POST creation of a new annotation
        #  Prima devo fare una ricerca sui video esistenti per avere l'id dell'item di un video
        #    a cui associare la annotazione 
        video_id = None
        item_id = None
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
                relationships = datas[0].get("relationships")
                if relationships is not None:
                    item = relationships.get("item")
                    if item is not None and item[0] is not None:
                        item_id = item[0].get("id")
                        # deve esistere l'item_id
                        assert item_id is not None
                        #log.debug("*** item id: " + item_id)
        log.info("*** Testing POST annotations")
        target_data = 'item:'+item_id
        body_data = {'type':'TextualBody','value':'testo della annotazione','language':'it'}
        selector_data = ''
        post_data = {'target':target_data,'body':body_data}
        # POST: try without log in
        res = client.post('/api/annotations', headers=None, data=json.dumps(post_data))
        assert res.status_code == hcodes.HTTP_BAD_UNAUTHORIZED 
        log.debug("*** Got http status " + str(hcodes.HTTP_BAD_UNAUTHORIZED))
        # POST: create a new annotation
        res = client.post('/api/annotations', headers=headers, data=json.dumps(post_data))
        assert res.status_code == hcodes.HTTP_OK_CREATED
        response = json.loads(res.data.decode('utf-8'))
        #log.debug("*** Response of post: "+json.dumps(response))
        if response is not None:
            data = response.get('Response', {}).get('data', {})
            if data is not None:
                anno_id = data
                #log.debug("*** created annotation with id: " + anno_id)
                # faccio get della annotation appena creata
                res = client.get('/api/annotations/'+anno_id, headers=headers)
                assert res.status_code == hcodes.HTTP_OK_BASIC
                content = json.loads(res.data.decode('utf-8'))
                #log.debug("*** Response of GET della annotations appena creata: "+json.dumps(content))

        # cancello la annotation appena creata
        if anno_id is not None:
            log.info("*** Testing DELETE annotation")
            res = client.delete('/api/annotations/'+anno_id, headers=headers)
            assert res.status_code == hcodes.HTTP_OK_NORESPONSE

    #################################################################
    # TODO mancano i test di creazione di una annotazione di uno shot 
    #       e di annotazione su una annotazione
    #################################################################


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