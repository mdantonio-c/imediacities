# -*- coding: utf-8 -*-

import json
from restapi.tests import BaseTests
from restapi.utilities.htmlcodes import hcodes
from restapi.utilities.logs import log


class TestApp(BaseTests):
    #
    # Al momento il metodo POST (Create a new video description) non
    #  fa nulla, quindi non faccio il test.
    # Non potendo creare una new video description non posso nemmeno
    #  testare la DELETE.
    #
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
        res = client.get('/api/videos')
        # This endpoint requires a valid authorization token
        assert res.status_code == hcodes.HTTP_BAD_UNAUTHORIZED
        # log.debug("*** Got http status " + str(hcodes.HTTP_BAD_UNAUTHORIZED))

        # log in
        log.debug("*** Do login")
        headers, _ = self.do_login(client, None, None)

        # GET videos without a specific id, get all videos
        res = client.get('/api/videos', headers=headers)
        assert res.status_code == hcodes.HTTP_OK_BASIC
        contents = json.loads(res.data.decode('utf-8'))
        # log.debug("*** Response of GET videos: "+json.dumps(contents))

        video_id = None
        if contents is not None:
            datas = contents.get('Response', {}).get('data', {})
            if datas is not None and datas[0] is not None:
                # datas e' una lista
                video_id = datas[0].get("id")
                # log.debug("*** videos[0] id: " + video_id)
        video_content = None
        # GET a video with a specific id
        if video_id is not None:
            res = client.get('/api/videos/' + video_id, headers=headers)
            assert res.status_code == hcodes.HTTP_OK_BASIC
            video_content = json.loads(res.data.decode('utf-8'))
            # log.debug("*** Response of GET videos with id: "+json.dumps(video_content))
            if video_content is not None:
                data = video_content.get('Response', {}).get('data', {})
                if data is not None and data[0] is not None:
                    # data e' una lista
                    video_title = data[0].get("attributes").get("identifying_title")
                    # log.debug("*** video title: " + video_title)
        log.info("*** Testing GET video shots")
        if video_id is not None:
            # try without log in
            res = client.get('/api/videos/' + video_id + '/shots')
            # This endpoint requires a valid authorization token
            assert res.status_code == hcodes.HTTP_BAD_UNAUTHORIZED
            # log.debug("*** Got http status " + str(hcodes.HTTP_BAD_UNAUTHORIZED))
            # GET shots
            res = client.get('/api/videos/' + video_id + '/shots', headers=headers)
            assert res.status_code == hcodes.HTTP_OK_BASIC
            shots_res = json.loads(res.data.decode('utf-8'))
            # log.debug("*** Response of GET video shots: "+json.dumps(shots_res))
            if shots_res is not None:
                shots_list = shots_res.get('Response', {}).get('data', {})
                # if shots_list is not None:
                # log.debug("*** number of shots: " + str(len(shots_list)))
                # if shots_list[0] is not None:
                # log.debug("*** shots[0]: " + json.dumps(shots_list[0]))

        log.info("*** Testing GET video annotations")
        if video_id is not None:
            # try without log in
            res = client.get('/api/videos/' + video_id + '/annotations')
            assert (
                res.status_code == hcodes.HTTP_BAD_UNAUTHORIZED
            )  # This endpoint requires a valid authorization token
            # log.debug("*** Got http status " + str(hcodes.HTTP_BAD_UNAUTHORIZED))
            # GET annotations
            res = client.get(
                '/api/videos/' + video_id + '/annotations', headers=headers
            )
            assert res.status_code == hcodes.HTTP_OK_BASIC
            anno_res = json.loads(res.data.decode('utf-8'))
            # log.debug("*** Response of GET video annotations: "+json.dumps(anno_res))
            if anno_res is not None:
                anno_list = anno_res.get('Response', {}).get('data', {})
                # if anno_list is not None:
                # log.debug("*** number of annotations: " + str(len(anno_list)))
                # if anno_list[0] is not None:
                # log.debug("*** annotations[0]: " + json.dumps(anno_list[0]))

        log.info("*** Testing GET video content")
        if video_id is not None:
            # GET content thumbnail
            # at the moment authorization token not required
            res = client.get('/api/videos/' + video_id + '/content?type=thumbnail')
            assert res.status_code == hcodes.HTTP_OK_BASIC
            # log.debug("*** Got http status " + str(hcodes.HTTP_OK_BASIC))
