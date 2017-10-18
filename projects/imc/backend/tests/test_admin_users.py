from utilities.logs import get_logger
from restapi.services.authentication import BaseAuthentication as ba
from utilities import htmlcodes as hcodes
from restapi.tests.utilities import AUTH_URI
import json


log = get_logger(__name__)

class TestApp:

    def test_admin_users(self, client): #client e' una fixture di pytest-flask
        """
            Test the API /api/admin/users
        """
        #
        # non e' prevista la possibilita' di fare get con uno specifico user_id
        #

        # log in
        log.debug("*** Do login")
        headers, _ = self.do_login(client, None, None)

        group_id = None
        group_shortname = None
        # /api/group viene usato per cercare i gruppi per nome, per 
        #  l'autocompletamento nel form dove si crea un nuovo user.
        # Chiamo prima questo per ottenere l'id del gruppo di test.
        # Infatti per creare uno nuovo user ci vuole un gruppo esistente...
        log.info("*** Search for the test group")
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
        # creo un nuovo utente
        log.info("*** Testing POST user")
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
                assert user_id is not None
        # modifica di un utente
        if user_id is not None:
            # PUT: modify the metadata of the new user
            log.info("*** Testing PUT user")
            put_data = { 'group': group_data, 'email':'test2@imediacities.org','name':'test2','password':'test2', 'surname':'test2'}
            res = client.put('/api/admin/users/'+user_id, headers=headers, data=json.dumps(put_data))
            assert res.status_code == hcodes.HTTP_OK_NORESPONSE

            # faccio il test della get e intanto verifico che la put abbia funzionato
            log.info("*** Testing GET users")
            # GET: try without log in
            res = client.get('/api/admin/users')
                # This endpoint requires a valid authorization token
            assert res.status_code == hcodes.HTTP_BAD_UNAUTHORIZED 
            log.debug("*** Got http status " + str(hcodes.HTTP_BAD_UNAUTHORIZED))
            # GET all users
            res = client.get('/api/admin/users', headers=headers)
            assert res.status_code == hcodes.HTTP_OK_BASIC
            contents = json.loads(res.data.decode('utf-8'))
            #log.debug("*** Response of GET users: "+json.dumps(contents))
            if contents is not None:
                datas = contents.get('Response', {}).get('data', {})
                # datas e' una lista
                if datas is not None:
                    #scorro la lista per trovare l'utente nuovo e verifico il name
                    for x in datas:
                        #log.debug("*** user: " + json.dumps(x))
                        if x.get("id") == user_id:
                            assert x.get("attributes").get("name") == 'test2'
                            break

        # cancello l'utente
        if user_id is not None:
            log.info("*** Testing DELETE user")
            res = client.delete('/api/admin/users/'+user_id, headers=headers)
            assert res.status_code == hcodes.HTTP_OK_NORESPONSE

    # a questo punto il database dovrebbe essere tornato come prima dei test

    ##############################
    # TODO mancano i test sui Role
    ##############################

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