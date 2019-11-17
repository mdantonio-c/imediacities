from restapi.utilities.logs import get_logger
from restapi.tests import BaseTests
from restapi.utilities.htmlcodes import hcodes
from restapi.tests.utilities import AUTH_URI
import json

log = get_logger(__name__)


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
        group_shortname = None
        res_group = client.get('/api/group/test', headers=headers)
        assert res_group.status_code == hcodes.HTTP_OK_BASIC
        contents_group = json.loads(res_group.data.decode('utf-8'))
        if contents_group is not None:
            datas_group = contents_group.get('Response', {}).get('data', {})
            if datas_group is not None and datas_group[0] is not None:
                # datas e' una lista
                group_id = datas_group[0].get("id")
                group_shortname = datas_group[0].get("shortname")
        # deve esistere il gruppo di test
        assert group_id is not None

        # mi serve il mio userid
        user_id = None
        log.info("*** Faccio get del profile")
        res_profile = client.get('/auth/profile', headers=headers)
        assert res_profile.status_code == hcodes.HTTP_OK_BASIC
        contents_profile = json.loads(res_profile.data.decode('utf-8'))
        if contents_profile is not None:
            # log.debug("*** Response of get profile: "+json.dumps(contents_profile))
            data_profile = contents_profile.get('Response', {}).get('data', {})
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
                'description': 'Role allowed to upload contents and metadata',
                'name': 'Archive',
            },
            {'description': 'Admin', 'name': 'admin_root'},
            {'description': 'automatic', 'name': 'normal_user'},
            {'description': 'automatic', 'name': 'staff_user'},
        ]
        group_data = {'id': group_id, 'shortname': group_shortname}
        put_data = {
            'group': group_data,
            'email': 'user@nomail.org',
            'name': 'Default',
            'password': 'test',
            'surname': 'User',
            'roles': roles,
        }
        res_put = client.put(
            '/api/admin/users/' + user_id, headers=headers, data=json.dumps(put_data)
        )
        assert res_put.status_code == hcodes.HTTP_OK_NORESPONSE

        log.info("*** Testing post /api/upload/")

        post_md_data = {
            'file': ('tests/custom/testdata/test_md_1234.xml', 'test_md_1234.xml'),
            'flowChunkNumber': 1,
            'flowFilename': 'test_md_1234.xml',
            'flowTotalChunks': 1,
            'flowChunkSize': 1,
        }
        res = client.post(
            '/api/upload',
            headers=headers,
            content_type='multipart/form-data',
            data=post_md_data,
        )
        assert res.status_code == hcodes.HTTP_OK_ACCEPTED
        contents = json.loads(res.data.decode('utf-8'))
        # log.debug("*** Response of post md file: "+json.dumps(contents))

        post_video_data = {
            'file': (
                'tests/custom/testdata/test_video_1234.mp4',
                'test_video_1234.mp4',
            ),
            'flowChunkNumber': 1,
            'flowFilename': 'test_video_1234.mp4',
            'flowTotalChunks': 1,
            'flowChunkSize': 1,
        }
        res2 = client.post(
            '/api/upload',
            headers=headers,
            content_type='multipart/form-data',
            data=post_video_data,
        )
        assert res2.status_code == hcodes.HTTP_OK_ACCEPTED
        contents2 = json.loads(res2.data.decode('utf-8'))
        # log.debug("*** Response of post video file: "+json.dumps(contents2))

        post_filetodel_data = {
            'file': ('tests/custom/testdata/to_del.txt', 'to_del.txt'),
            'flowChunkNumber': 1,
            'flowFilename': 'to_del.txt',
            'flowTotalChunks': 1,
            'flowChunkSize': 1,
        }
        res3 = client.post(
            '/api/upload',
            headers=headers,
            content_type='multipart/form-data',
            data=post_filetodel_data,
        )
        assert res3.status_code == hcodes.HTTP_OK_ACCEPTED
        contents3 = json.loads(res3.data.decode('utf-8'))
        # log.debug("*** Response of post todel file: "+json.dumps(contents3))
