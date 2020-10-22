import json

from restapi.tests import BaseTests
from restapi.utilities.logs import log


class TestApp(BaseTests):
    def test_POST(self, client):  # client e' una fixture di pytest-flask
        """
            Test POST method of /api/search
        """
        #
        # 1- fa POST search senza authorization token
        # 2- fa POST search con parametri type e term e pagination
        #

        log.info("*** Testing POST search")

        # try without log in
        res = client.post("/api/search")
        # This endpoint requires a valid authorization token
        assert res.status_code == 401

        # log in
        log.debug("*** Do login")
        headers, _ = self.do_login(client, None, None)

        # search all item of type video with pagination parameters
        post_data = {"type": "video", "term": "*"}
        res = client.post(
            "/api/search?size=10&page=1", headers=headers, data=json.dumps(post_data)
        )

        assert res.status_code == 200
