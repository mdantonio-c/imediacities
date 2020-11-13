"""
Expose the controlled vocabulary
"""
from imc.endpoints import IMCEndpoint
from restapi import decorators
from restapi.exceptions import NotFound
from restapi.utilities.logs import log


class Vocabulary(IMCEndpoint):

    labels = ["vocabulary"]

    @decorators.auth.require()
    @decorators.endpoint(
        path="/vocabulary",
        summary="Returns the controlled vocabulary.",
        responses={200: "The controlled vocabulary"},
    )
    def get(self, lang=None):
        """Get the controlled vocabulary."""
        log.debug("Loading the controlled vocabulary")
        try:
            f = open("../../scripts/convert-vocabulary/vocabulary.json")
        except FileNotFoundError:
            raise NotFound("Vocabulary not available")

        return f
