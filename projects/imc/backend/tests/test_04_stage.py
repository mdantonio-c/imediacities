import json
from restapi.tests import BaseTests
from restapi.utilities.htmlcodes import hcodes
from restapi.utilities.logs import log

import time


class TestApp(BaseTests):
    def test_stage_files(self, client):  # client e' una fixture di pytest-flask
        """
            Test API /api/stage
        """
        #
        # 1- fa GET di tutti gli stage files senza authorization token
        # 2- fa GET di tutti gli stage files con authorization token
        # 3- cerca il gruppo di test (che deve già esistere nel db)
        # 4- fa GET di tutti gli stage files by group, scorre la lista
        #     per trovare il file di metadati il cui nome inizia per 'test'
        # 5- lancia l'import del file troavato con mode=clean (viene analizzato
        #     il video e creati gli shot)
        # 6- cancello il file todel
        #

        log.info("*** Testing GET stage")
        # try without log in
        res = client.get('/api/stage')
        # This endpoint requires a valid authorization token
        assert res.status_code == hcodes.HTTP_BAD_UNAUTHORIZED
        # log.debug("*** Got http status " + str(hcodes.HTTP_BAD_UNAUTHORIZED))
        # log in
        log.debug("*** Do login")
        headers, _ = self.do_login(client, None, None)
        # GET all stage files
        res = client.get('/api/stage', headers=headers)
        assert res.status_code == hcodes.HTTP_OK_BASIC
        stage_content = json.loads(res.data.decode('utf-8'))
        # log.debug("*** Response of GET stage: "+json.dumps(stage_content))
        if stage_content is not None:
            element_list = stage_content.get('Response', {}).get('data', {})
            # if element_list is not None:
            # log.debug("*** Number of stage elements: " + str(len(element_list)))
            # log.debug("*** Stage elements: " + json.dumps(element_list))

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
                # log.debug("*** group: " + json.dumps(datas[0]))
                # deve esistere il gruppo di test
                assert group_id is not None

        filename = None
        # GET all stage files by group
        res2 = client.get('/api/stage/' + group_id, headers=headers)
        assert res2.status_code == hcodes.HTTP_OK_BASIC
        stage_content2 = json.loads(res2.data.decode('utf-8'))
        # log.debug("*** Response of GET stage with group id: "+json.dumps(stage_content2))
        if stage_content2 is not None:
            element_list2 = stage_content2.get('Response', {}).get('data', {})
            if element_list2 is not None:
                # log.debug("*** Number of stage elements of the test group: " + str(len(element_list2)))
                # log.debug("*** Stage elements of the test group: " + json.dumps(element_list2))
                # devo cercare un file di metadati per usarlo nella POST successiva
                for x in element_list2:
                    if x.get("type") == "metadata" and x.get("name").startswith('test'):
                        filename = x.get("name")
                        # log.debug("*** Metadata filename: "+json.dumps(filename))
                        break

        # il POST corrisponde all'import
        if filename is not None:
            log.info("*** Testing POST stage")
            # con mode=skip fa solo il caricamento dei metadati
            # lancio import con mode=clean così elabora il video e crea gli shot
            post_data = {'filename': filename, 'mode': 'clean'}
            res = client.post('/api/stage', headers=headers, data=json.dumps(post_data))
            assert res.status_code == hcodes.HTTP_OK_BASIC
            contents = json.loads(res.data.decode('utf-8'))
            # log.debug("*** Response of post stage: "+json.dumps(contents))
            if contents is not None:
                datas = contents.get('Response', {}).get('data', {})
        log.debug(
            "*** Start a pause of 20 sec to give time to the import task to finish..."
        )
        # metto una pausa per permettere all'import di terminare altrimenti i test successivi
        # non trovano i dati di cui hanno bisogno
        time.sleep(20)  # 20 sec
        log.debug("*** End of pause of 20 sec")

        # DELETE
        #  cancello il file todel
        if filename is not None:
            log.info("*** Testing DELETE file")
            post_data_delete = {'filename': 'to_del.txt'}
            res5 = client.delete(
                '/api/stage', headers=headers, data=json.dumps(post_data_delete)
            )
            assert res5.status_code == hcodes.HTTP_OK_NORESPONSE
            # log.debug("*** Deleted file: to_del.txt")
