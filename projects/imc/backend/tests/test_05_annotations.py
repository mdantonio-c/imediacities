import json

from restapi.tests import BaseTests
from restapi.utilities.logs import log


class TestApp(BaseTests):
    def test_annotations(self, client):  # client e' una fixture di pytest-flask
        """
            Test the API /api/annotations
        """
        #
        # 1- fa GET di tutte le annotation senza authorization token
        # 2- fa GET di tutte le annotation di tipo TVS, with pagination parameters
        # 3- fa GET di una annotations con uno specifico id
        # 4- fa una ricerca sui video esistenti per avere l'id dell'item di un video
        # 5- crea una nuova annotation sul video trovato senza authorization token
        # 6- crea una nuova annotation sul video trovato
        # 7- fa GET annotation by id con id della annotation appena creata
        # 8- crea una annotazione sulla annotazione appena creata
        # 9- cancella la annotazione di annotazione
        # 10- cancello la annotation sul video
        # 11- fa GET shots by video_id
        # 12- se trova almeno uno shot, prende il primo che trova e crea una
        #      annotazione sullo shot
        # 13- cancella la annotazione sullo shot
        #
        # A questo punto il database dovrebbe essere tornato
        #  come prima dei test
        #

        log.info("*** Testing GET annotations")
        # try without log in
        res = client.get("/api/annotations")
        # This endpoint requires a valid authorization token
        assert res.status_code == 401
        # log in
        log.debug("*** Do login")
        headers, _ = self.do_login(client, None, None)
        # GET all annotations of type TVS
        # res = client.get("/api/annotations?type=VIM", headers=headers)
        # assert res.status_code == 200
        # data = json.loads(res.data.decode("utf-8"))
        # # log.debug("*** Response of GET annotations: "+json.dumps(content))
        # anno_id = None
        # if data is not None and data[0] is not None:
        #     # data e' una lista
        #     anno_id = data[0].get("id")
        #     # log.debug("*** annotations[0] id: " + anno_id)
        # # GET an annotations with a specific id
        # if anno_id is not None:
        #     res = client.get("/api/annotations/" + anno_id, headers=headers)
        #     assert res.status_code == 200

        # POST creation of a new annotation on a video
        #  Prima devo fare una ricerca sui video esistenti
        # per avere l'id dell'item di un video
        #    a cui associare la annotazione
        video_id = None
        item_id = None
        res = client.get("/api/videos", headers=headers)
        assert res.status_code == 200
        datas = json.loads(res.data.decode("utf-8"))
        if datas is not None and datas[0] is not None:
            video_id = datas[0].get("id")
            # deve esistere almeno un video per fare i test
            assert video_id is not None
            # log.debug("*** videos[0] id: " + video_id)
            relationships = datas[0].get("relationships")
            if relationships is not None:
                item = relationships.get("item")
                if item is not None and item[0] is not None:
                    item_id = item[0].get("id")
                    # deve esistere l'item_id
                    assert item_id is not None
                    # log.debug("*** item id: " + item_id)
        log.info("*** Testing POST annotations")
        target_data = "item:" + item_id
        body_data = {
            "type": "TextualBody",
            "value": "testo della annotazione",
            "language": "it",
        }
        post_data = {"target": target_data, "body": body_data}
        # POST: try without log in
        res = client.post("/api/annotations", headers=None, data=json.dumps(post_data))
        assert res.status_code == 401
        # POST: create a new annotation
        res = client.post(
            "/api/annotations", headers=headers, data=json.dumps(post_data)
        )
        assert res.status_code == 201
        data = json.loads(res.data.decode("utf-8"))
        if data is not None:
            anno_id = data
            # log.debug("*** created annotation with id: " + anno_id)
            # faccio get della annotation appena creata
            res = client.get("/api/annotations/" + anno_id, headers=headers)
            assert res.status_code == 200

            # creo una annotazione sulla annotazione appena creata
            log.info("*** Testing annotation on an annotation")
            target_data2 = "anno:" + anno_id
            body_data2 = {
                "type": "TextualBody",
                "value": "testo della annotazione di annotazione",
                "language": "de",
            }
            post_data2 = {"target": target_data2, "body": body_data2}
            res2 = client.post(
                "/api/annotations", headers=headers, data=json.dumps(post_data2)
            )
            assert res2.status_code == 201
            anno_id2 = json.loads(res2.data.decode("utf-8"))
            # cancello la annotazione di annotazione
            if anno_id2 is not None:
                res2 = client.delete("/api/annotations/" + anno_id2, headers=headers)
                assert res2.status_code == 204

        # cancello la annotation appena creata
        if anno_id is not None:
            log.info("*** Testing DELETE annotation")
            res = client.delete("/api/annotations/" + anno_id, headers=headers)
            assert res.status_code == 204

        # creo annotazione su uno shot
        # prima devo trovare l'id di uno shot
        # lo cerco sul video che avevo usato prima
        log.info("*** Testing annotation on a shot")
        if video_id is not None:
            # GET shots
            res = client.get("/api/videos/" + video_id + "/shots", headers=headers)
            assert res.status_code == 200
            shots_list = json.loads(res.data.decode("utf-8"))
            if shots_list is not None:
                # log.debug("*** number of shots: " + str(len(shots_list)))
                if shots_list[0] is not None:
                    # log.debug("*** shots[0]: " + json.dumps(shots_list[0]))
                    shot_id = shots_list[0].get("id")
                    # deve esistere lo shot_id
                    assert shot_id is not None
                    # log.debug("*** shot id: " + shot_id)
                    # creo annotazione sullo shot
                    target_data3 = "shot:" + shot_id
                    body_data3 = {
                        "type": "TextualBody",
                        "value": "testo della annotazione di shot",
                        "language": "de",
                    }
                    post_data3 = {"target": target_data3, "body": body_data3}
                    res3 = client.post(
                        "/api/annotations",
                        headers=headers,
                        data=json.dumps(post_data3),
                    )
                    assert res3.status_code == 201
                    anno_id3 = json.loads(res3.data.decode("utf-8"))
                    # cancello la annotazione sullo shot
                    if anno_id3 is not None:
                        res3 = client.delete(
                            "/api/annotations/" + anno_id3, headers=headers
                        )
                        assert res3.status_code == 204

        # a questo punto il database dovrebbe essere tornato come prima dei test
