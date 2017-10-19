from utilities.logs import get_logger
from restapi.services.authentication import BaseAuthentication as ba
from utilities import htmlcodes as hcodes
from restapi.tests.utilities import AUTH_URI
import json


log = get_logger(__name__)

class TestApp:

    def test_stage_files(self, client): #client e' una fixture di pytest-flask
        """
            Test API /api/stage
        """
        log.info("*** Testing GET stage")
        # try without log in
        res = client.get('/api/stage')
        # This endpoint requires a valid authorization token
        assert res.status_code == hcodes.HTTP_BAD_UNAUTHORIZED
        log.debug("*** Got http status " + str(hcodes.HTTP_BAD_UNAUTHORIZED))
        # log in
        log.debug("*** Do login")
        headers, _ = self.do_login(client, None, None)
        # GET all stage files
        res = client.get('/api/stage', headers=headers)
        assert res.status_code == hcodes.HTTP_OK_BASIC
        stage_content = json.loads(res.data.decode('utf-8'))
        #log.debug("*** Response of GET stage: "+json.dumps(stage_content))
        if stage_content is not None:
            element_list = stage_content.get('Response', {}).get('data', {})
            if element_list is not None:
                log.debug("*** Number of stage elements: " + str(len(element_list)))
                #log.debug("*** Stage elements: " + json.dumps(element_list))

        log.info("*** Search for the test group")
        group_id = None
        res = client.get('/api/group/test', headers=headers)
        assert res.status_code == hcodes.HTTP_OK_BASIC
        contents = json.loads(res.data.decode('utf-8'))
        if contents is not None:
            datas = contents.get('Response', {}).get('data', {})
            if datas is not None and datas[0] is not None:
                # datas e' una lista
                group_id = datas[0].get("id")
                #log.debug("*** group: " + json.dumps(datas[0]))
                # deve esistere il gruppo di test
                assert group_id is not None

        filename = None
        # GET all stage files by group
        res2 = client.get('/api/stage/'+group_id, headers=headers)
        assert res2.status_code == hcodes.HTTP_OK_BASIC
        stage_content2 = json.loads(res2.data.decode('utf-8'))
        #log.debug("*** Response of GET stage with group id: "+json.dumps(stage_content2))
        if stage_content2 is not None:
            element_list2 = stage_content2.get('Response', {}).get('data', {})
            if element_list2 is not None:
                log.debug("*** Number of stage elements of the test group: " + str(len(element_list2)))
                #log.debug("*** Stage elements of the test group: " + json.dumps(element_list2))
                #devo cercare un file che sia un video per usarlo nella POST
                for x in element_list2:
                    if x.get("type") == "metadata":
                        filename = x.get("name")
                        #log.debug("*** Metadata filename: "+json.dumps(filename))
                        break

        # il POST corrisponde all'import
        if filename is not None:
            log.info("*** Testing POST stage")
            # lancio import in mode skip così fa solo il caricamento dei metadati
            post_data = { 'filename': filename, 'mode':'skip'}
            res = client.post('/api/stage', headers=headers, data=json.dumps(post_data))
            assert res.status_code == hcodes.HTTP_OK_BASIC
            contents = json.loads(res.data.decode('utf-8'))
            #log.debug("*** Response of post stage: "+json.dumps(contents))
            if contents is not None:
                datas = contents.get('Response', {}).get('data', {})
                if datas is not None:
                    task_id=datas
                    log.debug("*** Import task id: "+json.dumps(task_id))

        # TODO test DELETE
        #  Al momento non riesco a creare dei file quindi non posso 
        #   testare la cancellazione

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