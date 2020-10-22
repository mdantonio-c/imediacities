import json
import time

from restapi.tests import BaseTests
from restapi.utilities.htmlcodes import hcodes
from restapi.utilities.logs import log


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
        res = client.get("/api/stage")
        # This endpoint requires a valid authorization token
        assert res.status_code == 401
        # log in
        log.debug("*** Do login")
        headers, _ = self.do_login(client, None, None)
        # GET all stage files
        res = client.get("/api/stage", headers=headers)
        assert res.status_code == 200
        # stage_content = json.loads(res.data.decode("utf-8"))

        log.info("*** Search for the test group")
        group_id = None
        resp = client.get("/api/admin/groups", headers=headers)
        assert resp.status_code == 200
        groups = json.loads(resp.data.decode("utf-8"))
        for g in groups:
            if g.get("shortname") != "default":
                continue
            group_id = g.get("uuid")
        # deve esistere il gruppo di test
        assert group_id is not None

        filename = None
        # GET all stage files by group
        res2 = client.get("/api/stage/" + group_id, headers=headers)
        assert res2.status_code == 200
        stage_content2 = json.loads(res2.data.decode("utf-8"))
        if stage_content2 is not None:
            # devo cercare un file di metadati per usarlo nella POST successiva
            for x in stage_content2:
                if x.get("type") == "metadata" and x.get("name").startswith("test"):
                    filename = x.get("name")
                    # log.debug("*** Metadata filename: "+json.dumps(filename))
                    break

        # il POST corrisponde all'import
        if filename is not None:
            log.info("*** Testing POST stage")
            # con mode=skip fa solo il caricamento dei metadati
            # lancio import con mode=clean così elabora il video e crea gli shot
            post_data = {"filename": filename, "mode": "clean"}
            res = client.post("/api/stage", headers=headers, data=json.dumps(post_data))
            assert res.status_code == 200
            # log.debug("*** Response of post stage: "+json.dumps(contents))
        log.debug(
            "*** Start a pause of 20 sec to give time to the import task to finish..."
        )
        # non trovano i dati di cui hanno bisogno
        time.sleep(20)  # 20 sec
        log.debug("*** End of pause of 20 sec")

        # DELETE
        #  cancello il file todel
        if filename is not None:
            log.info("*** Testing DELETE file")
            post_data_delete = {"filename": "to_del.txt"}
            res5 = client.delete(
                "/api/stage", headers=headers, data=json.dumps(post_data_delete)
            )
            assert res5.status_code == 204
            # log.debug("*** Deleted file: to_del.txt")
