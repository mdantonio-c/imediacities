import json

from restapi.tests import BaseTests
from restapi.utilities.htmlcodes import hcodes
from restapi.utilities.logs import log


class TestApp(BaseTests):
    def test_get(self, client):  # client e' una fixture di pytest-flask
        """
            Test GET method of /api/videos
        """
        #
        # 1- fa GET di tutti i video senza authorization token
        # 2- fa GET di tutti i video con authorization token
        # 3- fa GET di un video con uno specifico id
        # 4- fa GET di tutti gli shots by video_id senza authorization token
        # 5- fa GET di tutti gli shots by video_id con authorization token
        # 6- fa GET di tutte le annotation by video_id senza authorization token
        # 7- fa GET di tutte le annotation by video_id con authorization token
        # 8- fa GET della thumbnail di un video
        #

        log.info("*** Testing GET videos")
        # try without log in
        res = client.get("/api/videos")
        # This endpoint requires a valid authorization token
        assert res.status_code == 401

        # log in
        log.debug("*** Do login")
        headers, _ = self.do_login(client, None, None)

        # GET videos without a specific id, get all videos
        res = client.get("/api/videos", headers=headers)
        assert res.status_code == 200
        datas = json.loads(res.data.decode("utf-8"))

        video_id = None
        if datas is not None and datas[0] is not None:
            # datas e' una lista
            video_id = datas[0].get("id")
            # log.debug("*** videos[0] id: " + video_id)

        # GET a video with a specific id
        if video_id is not None:
            res = client.get("/api/videos/" + video_id, headers=headers)
            assert res.status_code == 200

        log.info("*** Testing GET video shots")
        if video_id is not None:
            # try without log in
            res = client.get("/api/videos/" + video_id + "/shots")
            # This endpoint requires a valid authorization token
            assert res.status_code == 401
            # GET shots
            res = client.get("/api/videos/" + video_id + "/shots", headers=headers)
            assert res.status_code == 200

        log.info("*** Testing GET video annotations")
        if video_id is not None:
            # try without log in
            res = client.get("/api/videos/" + video_id + "/annotations")
            assert (
                res.status_code == 401
            )  # This endpoint requires a valid authorization token
            # GET annotations
            res = client.get(
                "/api/videos/" + video_id + "/annotations", headers=headers
            )
            assert res.status_code == 200

        log.info("*** Testing GET video content")
        if video_id is not None:
            # GET content thumbnail
            # at the moment authorization token not required
            res = client.get("/api/videos/" + video_id + "/content?type=thumbnail")
            assert res.status_code == 200
