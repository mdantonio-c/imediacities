# -*- coding: utf-8 -*-

"""
Expose the controlled vocabulary
"""
from restapi.utilities.logs import get_logger
from restapi.rest.definition import EndpointResource
from restapi.exceptions import RestApiException
from restapi.protocols.bearer import authentication
from restapi.utilities.htmlcodes import hcodes
from restapi import decorators as decorate

log = get_logger(__name__)


class Vocabulary(EndpointResource):

    # schema_expose = True
    labels = ['vocabulary']
    GET = {'/vocabulary': {'summary': 'Returns the controlled vocabulary.', 'responses': {'200': {'description': 'The controlled vocabulary'}, '401': {'description': 'This endpoint requires a valid authorization token.'}, '500': {'description': 'An unexpected error occured.'}}}}

    @decorate.catch_error()
    @authentication.required()
    def get(self, lang=None):
        """Get the controlled vocabulary."""
        log.debug('load the controlled vocabulary')
        try:
            f = open("../../scripts/convert-vocabulary/vocabulary.json", "r")
        except FileNotFoundError:
            log.warning('Vocabulary file not found')
            raise RestApiException(
                "Warining: vocabulary not available",
                status_code=hcodes.HTTP_BAD_NOTFOUND,
            )

        return f
