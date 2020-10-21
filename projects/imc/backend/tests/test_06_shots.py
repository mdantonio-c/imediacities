import json

from restapi.tests import BaseTests
from restapi.utilities.htmlcodes import hcodes
from restapi.utilities.logs import log


class TestApp(BaseTests):
    def test_get(self, client):  # client e' una fixture di pytest-flask
        """
            Test GET method of /api/shots
        """
        #
        # 1- fa GET di tutti i video
        # 2- fa GET di tutti gli shot by video_id
        # 3- fa GET shot by id
        # 4- fa GET shot thumbnail
        #

        #  Prima devo fare una ricerca sui video esistenti per trovare un video
        #    di cui prendere uno shot per avere lo shot_id
        video_id = None
        shot_id = None
        # log in
        log.debug("*** Do login")
        headers, _ = self.do_login(client, None, None)
        res = client.get("/api/videos", headers=headers)
        assert res.status_code == hcodes.HTTP_OK_BASIC
        datas = json.loads(res.data.decode("utf-8"))
        if datas is not None and datas[0] is not None:
            video_id = datas[0].get("id")
            # deve esistere almeno un video per fare i test
            assert video_id is not None
            # log.debug("*** videos[0] id: " + video_id)
            # GET shots
            res = client.get("/api/videos/" + video_id + "/shots", headers=headers)
            assert res.status_code == hcodes.HTTP_OK_BASIC
            shots_list = json.loads(res.data.decode("utf-8"))
            if shots_list is not None:
                # log.debug("*** number of shots: " + str(len(shots_list)))
                if shots_list[0] is not None:
                    # log.debug("*** shots[0]: " + json.dumps(shots_list[0]))
                    shot_id = shots_list[0].get("id")
                    # deve esistere lo shot_id
                    assert shot_id is not None
                    # log.debug("*** shot id: " + shot_id)
        if shot_id is not None:
            log.info("*** Testing GET shot by id")
            # GET a shot with a specific id
            # at the moment authorization token not required for GET shot
            res = client.get("/api/shots/" + shot_id)
            assert res.status_code == hcodes.HTTP_OK_BASIC
            log.info("*** Testing GET shot thumbnail")
            # GET shot thumbnail
            res = client.get("/api/shots/" + shot_id + "?content=thumbnail")
            assert res.status_code == hcodes.HTTP_OK_BASIC
            # log.debug("*** Got http status " + str(hcodes.HTTP_OK_BASIC))
