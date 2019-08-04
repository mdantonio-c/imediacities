# -*- coding: utf-8 -*-

"""
Expose the controlled vocabulary
"""
import os, json
from utilities.logs import get_logger
from restapi.rest.definition import EndpointResource
from restapi.exceptions import RestApiException
from utilities import htmlcodes as hcodes
from restapi import decorators as decorate

log = get_logger(__name__)


class Vocabulary(EndpointResource):
    @decorate.catch_error()
    def get(self, lang=None):
        """Get the controlled vocabulary."""
        log.debug('load the controlled vocabulary')
        try:
            f = open("../../scripts/convert-vocabulary/vocabulary.json", "r")
        except FileNotFoundError as err:
            log.warning('Vocabulary file not found')
            raise RestApiException(
                "Warining: vocabulary not available",
                status_code=hcodes.HTTP_BAD_NOTFOUND,
            )
