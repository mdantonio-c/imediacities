# -*- coding: utf-8 -*-

"""
Expose the codelists
"""
import os, json
from utilities.logs import get_logger
from restapi.rest.definition import EndpointResource
from restapi.exceptions import RestApiException
from utilities import htmlcodes as hcodes
from restapi import decorators as decorate

log = get_logger(__name__)

class Fcodelist(EndpointResource):

    @decorate.catch_error()
    def get(self, codelist=None):
        """Get the codelists."""
        log.debug('load the codelist: '+codelist)
        input_parameters = self.get_input()
        lang = input_parameters['lang']
        if lang is None:
            lang='en'
        filename = codelist + '.json'
        filepath = 'imc/fcodelist/' + lang + '/' + filename
        log.debug('filepath: '+filepath)
        try:
            data = json.load(open(filepath))
            return self.force_response(data)            
        except FileNotFoundError as err:
            log.warning('Codelist file not found: '+filepath)
            raise RestApiException(
                    "Warning: codelist not available",
                    status_code=hcodes.HTTP_BAD_NOTFOUND)
