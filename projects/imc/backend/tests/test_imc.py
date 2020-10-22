from restapi.tests import BaseTests

# from restapi.utilities.logs import log


class TestApp(BaseTests):
    def test_status(self, client):

        res = client.get("/api/stage")
        assert res.status_code == 401

        headers, _ = self.do_login(client, None, None)
        res = client.get("/api/stage", headers=headers)

        assert res.status_code == 200
