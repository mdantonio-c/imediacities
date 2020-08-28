"""
Expose the codelists
"""
import json

from imc.endpoints import IMCEndpoint
from restapi import decorators
from restapi.exceptions import RestApiException
from restapi.models import fields
from restapi.utilities.htmlcodes import hcodes
from restapi.utilities.logs import log


class Fcodelist(IMCEndpoint):

    labels = ["fcodelist"]

    @decorators.auth.require()
    @decorators.use_kwargs(
        {
            "lang": fields.Str(
                required=False, missing="en", description="Language of the codelist"
            )
        },
        location="query",
    )
    @decorators.endpoint(
        path="/fcodelist/<codelist>",
        summary="Get codelists",
        description="Returns a codelist",
        responses={200: "A codelist.", 404: "Codelist does not exist."},
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
