from utilities.logs import get_logger
from restapi.services.authentication import BaseAuthentication as ba
from utilities import htmlcodes as hcodes
from restapi.tests.utilities import AUTH_URI
import json


log = get_logger(__name__)

class TestApp:

    def test_admin_groups(self, client): #client e' una fixture di pytest-flask
        """
            Test the API /api/admin/groups
        """
        #
        # non e' prevista la possibilita' di fare get con uno specifico group_id
        #

        # log in
        log.debug("*** Do login")
        headers, _ = self.do_login(client, None, None)

        group_id = None
        group_shortname = None
        # /api/group viene usato per cercare i gruppi per nome, per 
        #  l'autocompletamento nel form dove si crea un nuovo user.
        # Chiamo prima questo per ottenere l'id del gruppo di test.
        # Infatti per creare un nuovo gruppo ci vuole uno user esistente e per
        #  creare uno nuovo user ci vuole un gruppo esistente...
        log.info("*** Testing get /api/group/")
        res = client.get('/api/group/test', headers=headers)
        assert res.status_code == hcodes.HTTP_OK_BASIC
        contents = json.loads(res.data.decode('utf-8'))
        if contents is not None:
            datas = contents.get('Response', {}).get('data', {})
            if datas is not None and datas[0] is not None:
                # datas e' una lista
                group_id = datas[0].get("id")
                group_shortname = datas[0].get("shortname")
        # deve esistere il gruppo di test
        assert group_id is not None

        user_id=None
        # creo un nuovo utente per i test
        log.info("*** Creating user test")
        group_data = {'id': group_id , 'shortname': group_shortname}
        post_user_data = { 'group': group_data, 'email':'test@imediacities.org','name':'test','password':'test', 'surname':'test'}
        res = client.post('/api/admin/users', headers=headers, data=json.dumps(post_user_data))
        assert res.status_code == hcodes.HTTP_OK_BASIC
        contents = json.loads(res.data.decode('utf-8'))
        #log.debug("*** Response of post new user: "+json.dumps(contents))
        if contents is not None:
            datas = contents.get('Response', {}).get('data', {})
            if datas is not None:
                user_id = datas
        # test della creazione di un nuovo gruppo e della sua modifica
        if user_id is not None:
            new_group_id = None
            log.info("*** Testing POST group")
            post_data = {'shortname':'test_group','fullname':'TEST_GROUP','coordinator':user_id}
            # POST: try without log in
            res = client.post('/api/admin/groups', headers=None, data=json.dumps(post_data))
            assert res.status_code == hcodes.HTTP_BAD_UNAUTHORIZED 
            log.debug("*** Got http status " + str(hcodes.HTTP_BAD_UNAUTHORIZED))
            # POST: create a new group
            res = client.post('/api/admin/groups', headers=headers, data=json.dumps(post_data))
            assert res.status_code == hcodes.HTTP_OK_BASIC
            response = json.loads(res.data.decode('utf-8'))
            #log.debug("*** Response of post: "+json.dumps(response))
            if response is not None:
                new_group_id = response.get('Response', {}).get('data', {})
            if new_group_id is not None:
                # PUT: modify the metadata of the new group
                log.info("*** Testing PUT group")
                put_data = {'shortname':'test_group_2','fullname':'TEST_GROUP_2','coordinator':user_id}
                res = client.put('/api/admin/groups/'+new_group_id, headers=headers, data=json.dumps(put_data))
                assert res.status_code == hcodes.HTTP_OK_NORESPONSE

                # faccio il test della get e intanto verifico che la put abbia funzionato
                log.info("*** Testing GET groups")
                # GET: try without log in
                res = client.get('/api/admin/groups')
                # This endpoint requires a valid authorization token
                assert res.status_code == hcodes.HTTP_BAD_UNAUTHORIZED 
                log.debug("*** Got http status " + str(hcodes.HTTP_BAD_UNAUTHORIZED))
                # GET all groups
                res = client.get('/api/admin/groups', headers=headers)
                assert res.status_code == hcodes.HTTP_OK_BASIC
                contents = json.loads(res.data.decode('utf-8'))
                #log.debug("*** Response of GET groups: "+json.dumps(contents))
                if contents is not None:
                    datas = contents.get('Response', {}).get('data', {})
                    # datas e' una lista
                    if datas is not None:
                        #scorro la lista per trovare il gruppo nuovo e verifico lo shortname
                        for x in datas:
                            #log.debug("*** group: " + json.dumps(x))
                            if x.get("id") == new_group_id:
                                assert x.get("attributes").get("shortname") == 'test_group_2'
                                break

                # DELETE: delete the new group
                log.info("*** Testing DELETE group")
                res = client.delete('/api/admin/groups/'+new_group_id, headers=headers)
                assert res.status_code == hcodes.HTTP_OK_NORESPONSE

        # cancello l'utente creato per questi test
        if user_id is not None:
            log.info("*** DELETE user test")
            res = client.delete('/api/admin/users/'+user_id, headers=headers)
            assert res.status_code == hcodes.HTTP_OK_NORESPONSE

    # a questo punto il database dovrebbe essere tornato come prima dei test
   
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