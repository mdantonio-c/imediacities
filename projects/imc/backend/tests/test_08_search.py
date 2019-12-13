# -*- coding: utf-8 -*-

import json
from restapi.tests import BaseTests
from restapi.utilities.htmlcodes import hcodes
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
        res = client.post('/api/search')
        # This endpoint requires a valid authorization token
        assert res.status_code == hcodes.HTTP_BAD_UNAUTHORIZED
        # log.debug("*** Got http status " + str(hcodes.HTTP_BAD_UNAUTHORIZED))

        # log in
        log.debug("*** Do login")
        headers, _ = self.do_login(client, None, None)

        # search all item of type video with pagination parameters
        post_data = {'type': 'video', 'term': '*'}
        res = client.post(
            '/api/search?perpage=10&currentpage=1',
            headers=headers,
            data=json.dumps(post_data),
        )

        assert res.status_code == hcodes.HTTP_OK_BASIC
        response = json.loads(res.data.decode('utf-8'))
        # log.debug("*** Response of search: "+json.dumps(response))

        if response is not None:
            videos_data = response.get('Response', {}).get('data', {})
            # if videos_data is not None:
            #     log.debug("*** Number of videos found: " + str(len(videos_data)))
