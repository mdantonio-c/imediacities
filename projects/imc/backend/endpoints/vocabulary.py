"""
Expose the controlled vocabulary
"""
from imc.endpoints import IMCEndpoint
from restapi import decorators
from restapi.exceptions import NotFound
from restapi.rest.definition import Response
from restapi.services.authentication import User
from restapi.utilities.logs import log


class Vocabulary(IMCEndpoint):

    labels = ["vocabulary"]

    @decorators.auth.require()
    @decorators.endpoint(
        path="/vocabulary",
        summary="Returns the controlled vocabulary.",
        responses={200: "The controlled vocabulary"},
    )
    def get(self, user: User) -> Response:
        """Get the controlled vocabulary."""
        log.debug("Loading the controlled vocabulary")
        try:
            open("../../scripts/convert-vocabulary/vocabulary.json")
        except FileNotFoundError:
            raise NotFound("Vocabulary not available")

        return self.response("not implemented yet")
