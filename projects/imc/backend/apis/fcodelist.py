"""
Expose the codelists
"""
import json

from imc.apis import IMCEndpoint
from restapi import decorators
from restapi.exceptions import RestApiException
from restapi.models import fields
from restapi.utilities.htmlcodes import hcodes
from restapi.utilities.logs import log


class Fcodelist(IMCEndpoint):

    labels = ["fcodelist"]
    _GET = {
        "/fcodelist/<codelist>": {
            "summary": "GET codelists",
            "description": "Returns a codelist",
            "responses": {
                "200": {"description": "A codelist."},
                "404": {"description": "Codelist does not exist."},
            },
        }
    }

    @decorators.auth.require()
    @decorators.use_kwargs(
        {
            "lang": fields.Str(
                required=False, missing="en", description="Language of the codelist"
            )
        },
        locations=["query"],
    )
    def get(self, codelist, lang):
        """Get the codelists."""
        log.debug("load the codelist: " + codelist)
        filename = codelist + ".json"
        filepath = "imc/fcodelist/" + lang + "/" + filename
        log.debug("filepath: " + filepath)
        try:
            data = json.load(open(filepath))
            return self.response(data)
        except FileNotFoundError:
            log.warning("Codelist file not found: " + filepath)
            raise RestApiException(
                "Warning: codelist not available", status_code=hcodes.HTTP_BAD_NOTFOUND
            )
