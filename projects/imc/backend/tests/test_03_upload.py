import json

from restapi.tests import BaseTests
from restapi.utilities.htmlcodes import hcodes
from restapi.utilities.logs import log


class TestApp(BaseTests):
    def test_upload(self, client):  # client e' una fixture di pytest-flask
        """
            Test the API /api/upload
        """
        #
        # Fa l'upload di un video e dei suoi metadati che serviranno
        #  per i test delle altre apis, e anche di un file che servirà
        #  per testare la cancellazione
        #
        # Per poter uploadare dei file l'utente deve avere Role di Archive
        #  e appartenere a un gruppo
        #

        # log in
        log.debug("*** Do login")
        headers, _ = self.do_login(client, None, None)

        log.info("*** Cerco il gruppo di test")
        group_id = None
        resp = client.get("/api/admin/groups", headers=headers)
        assert resp.status_code == hcodes.HTTP_OK_BASIC
        groups = json.loads(resp.data.decode("utf-8"))
        for g in groups:
            if g.get("shortname") != "default":
                continue
            group_id = g.get("uuid")
        # deve esistere il gruppo di test
        assert group_id is not None

        # mi serve il mio userid
        user_id = None
        log.info("*** Faccio get del profile")
        res_profile = client.get("/auth/profile", headers=headers)
        assert res_profile.status_code == hcodes.HTTP_OK_BASIC
        data_profile = json.loads(res_profile.data.decode("utf-8"))
        if data_profile is not None:
            # log.debug("*** Data of get profile: "+json.dumps(data_profile))
            if data_profile.get("uuid") is not None:
                user_id = data_profile.get("uuid")
                # log.debug("*** user_id: "+json.dumps(user_id))
        # il mio user_id deve esistere
        assert user_id is not None

        # modifico l'utente di default (con il quale sono loggato) per assegnargli
        #  role 'Archive' e associarlo al gruppo di test
        roles = [
            {
                "description": "Role allowed to upload contents and metadata",
                "name": "Archive",
            },
            {"description": "Admin", "name": "admin_root"},
            {"description": "automatic", "name": "normal_user"},
            {"description": "automatic", "name": "staff_user"},
        ]
        put_data = {
            "group": group_id,
            "email": "user@nomail.org",
            "name": "Default",
            "password": "test",
            "surname": "User",
            "roles": roles,
        }
        res_put = client.put(
            "/api/admin/users/" + user_id, headers=headers, data=json.dumps(put_data)
        )
        assert res_put.status_code == hcodes.HTTP_OK_NORESPONSE

        log.info("*** Testing post /api/upload/")

        post_md_data = {
            "file": ("tests/custom/testdata/test_md_1234.xml", "test_md_1234.xml"),
            "flowChunkNumber": 1,
            "flowFilename": "test_md_1234.xml",
            "flowTotalChunks": 1,
            "flowChunkSize": 1,
        }
        res = client.post(
            "/api/upload",
            headers=headers,
            content_type="multipart/form-data",
            data=post_md_data,
        )
        assert res.status_code == hcodes.HTTP_OK_ACCEPTED
        json.loads(res.data.decode("utf-8"))

        post_video_data = {
            "file": (
                "tests/custom/testdata/test_video_1234.mp4",
                "test_video_1234.mp4",
            ),
            "flowChunkNumber": 1,
            "flowFilename": "test_video_1234.mp4",
            "flowTotalChunks": 1,
            "flowChunkSize": 1,
        }
        res2 = client.post(
            "/api/upload",
            headers=headers,
            content_type="multipart/form-data",
            data=post_video_data,
        )
        assert res2.status_code == hcodes.HTTP_OK_ACCEPTED
        json.loads(res2.data.decode("utf-8"))

        post_filetodel_data = {
            "file": ("tests/custom/testdata/to_del.txt", "to_del.txt"),
            "flowChunkNumber": 1,
            "flowFilename": "to_del.txt",
            "flowTotalChunks": 1,
            "flowChunkSize": 1,
        }
        res3 = client.post(
            "/api/upload",
            headers=headers,
            content_type="multipart/form-data",
            data=post_filetodel_data,
        )
        assert res3.status_code == hcodes.HTTP_OK_ACCEPTED
        json.loads(res3.data.decode("utf-8"))
