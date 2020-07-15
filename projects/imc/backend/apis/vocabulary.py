"""
Expose the controlled vocabulary
"""
from imc.apis import IMCEndpoint
from restapi import decorators
from restapi.exceptions import RestApiException
from restapi.utilities.htmlcodes import hcodes
from restapi.utilities.logs import log


class Vocabulary(IMCEndpoint):

    labels = ["vocabulary"]
    _GET = {
        "/vocabulary": {
            "summary": "Returns the controlled vocabulary.",
            "responses": {"200": {"description": "The controlled vocabulary"}},
        }
    }

    @decorators.auth.required()
    def get(self, lang=None):
        """Get the controlled vocabulary."""
        log.debug("load the controlled vocabulary")
        try:
            f = open("../../scripts/convert-vocabulary/vocabulary.json")
        except FileNotFoundError:
            log.warning("Vocabulary file not found")
            raise RestApiException(
                "Warining: vocabulary not available",
                status_code=hcodes.HTTP_BAD_NOTFOUND,
            )

        return f
