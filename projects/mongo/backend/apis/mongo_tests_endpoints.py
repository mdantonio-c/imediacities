# -*- coding: utf-8 -*-

"""
An endpoint example
"""

# from flask import current_app
from restapi.rest.definition import EndpointResource

from utilities.logs import get_logger

log = get_logger(__name__)


# if current_app.config['TESTING']:
class DoTests(EndpointResource):

    def get(self):
        mongo = self.get_service_instance('mongo')
        print(mongo)
        log.warning("a call")
        return self.force_response('Hello world!')
