# -*- coding: utf-8 -*-

import json
from restapi.tests import BaseTests
from utilities import htmlcodes as hcodes
from utilities.logs import get_logger

log = get_logger(__name__)


class TestApp(BaseTests):
    def test_admin_users(self, client):  # client e' una fixture di pytest-flask
        """
            Test the API /api/admin/users
        """
        #
        # 1- cerca il gruppo di test (che deve già esistere nel db)
        # 2- cerca i Role esistenti
        # 3- creo un nuovo utente
        # 4- modifica il nuovo utente
        # 5- fa GET di tutti gli utenti senza authorization token
        # 6- fa get di tutti gli utenti con authorization token, scorre la lista per trovare
        #     il nuovo utente e verifica che la precedente modifica
        #     abbia funzionato
        # 7- cancella il nuovo utente
        #
        # A questo punto il database dovrebbe essere tornato
        #  come prima dei test
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
        #
        # Non e' prevista la possibilita' di fare get con uno specifico user_id
        #
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

        # cerco i Role esistenti
        log.info("*** Search for the roles")
        res2 = client.get('/api/role/a', headers=headers)
        assert res2.status_code == hcodes.HTTP_OK_BASIC
        contents2 = json.loads(res2.data.decode('utf-8'))
        if contents2 is not None:
            datas2 = contents2.get('Response', {}).get('data', {})
            if datas2 is not None:
                # datas2 e' una lista
                roles = datas2
                # log.debug("*** roles: "+json.dumps(roles))

        user_id = None
        # creo un nuovo utente
        log.info("*** Testing POST user")
        group_data = {'id': group_id, 'shortname': group_shortname}
        post_user_data = {
            'group': group_data,
            'email': 'test@imediacities.org',
            'name': 'test',
            'password': 'test',
            'surname': 'test',
            'roles': [],
        }
        res = client.post(
            '/api/admin/users', headers=headers, data=json.dumps(post_user_data)
        )
        assert res.status_code == hcodes.HTTP_OK_BASIC
        contents = json.loads(res.data.decode('utf-8'))
        # log.debug("*** Response of post new user: "+json.dumps(contents))
        if contents is not None:
            datas = contents.get('Response', {}).get('data', {})
            if datas is not None:
                user_id = datas
                assert user_id is not None
        # modifica di un utente
        if user_id is not None:
            # PUT: modify the metadata of the new user
            log.info("*** Testing PUT user")
            put_data = {
                'group': group_data,
                'email': 'test2@imediacities.org',
                'name': 'test2',
                'password': 'test2',
                'surname': 'test2',
                'roles': roles,
            }
            res = client.put(
                '/api/admin/users/' + user_id,
                headers=headers,
                data=json.dumps(put_data),
            )
            assert res.status_code == hcodes.HTTP_OK_NORESPONSE

            # faccio il test della get e intanto verifico che la put abbia funzionato
            log.info("*** Testing GET users")
            # GET: try without log in
            res = client.get('/api/admin/users')
            # This endpoint requires a valid authorization token
            assert res.status_code == hcodes.HTTP_BAD_UNAUTHORIZED
            # log.debug("*** Got http status " + str(hcodes.HTTP_BAD_UNAUTHORIZED))
            # GET all users
            res = client.get('/api/admin/users', headers=headers)
            assert res.status_code == hcodes.HTTP_OK_BASIC
            contents = json.loads(res.data.decode('utf-8'))
            # log.debug("*** Response of GET users: "+json.dumps(contents))
            if contents is not None:
                datas = contents.get('Response', {}).get('data', {})
                # datas e' una lista
                if datas is not None:
                    # scorro la lista per trovare l'utente nuovo e verifico il name
                    for x in datas:
                        if x.get("id") == user_id:
                            # log.debug("*** user: " + json.dumps(x))
                            assert x.get("attributes").get("name") == 'test2'
                            break

        # cancello l'utente
        if user_id is not None:
            log.info("*** Testing DELETE user")
            res = client.delete('/api/admin/users/' + user_id, headers=headers)
            assert res.status_code == hcodes.HTTP_OK_NORESPONSE

    # a questo punto il database dovrebbe essere tornato come prima dei test
