# -*- coding: utf-8 -*-

"""
An endpoint example
"""

from commons.logs import get_logger
from ..base import ExtendedApiResource
from .. import decorators as decorate
# from ...auth import authentication
# from flask_restful import request
# from commons import htmlcodes as hcodes
# from commons.services.uuid import getUUID

logger = get_logger(__name__)


#####################################
class Upload(ExtendedApiResource):

    # @authentication.authorization_required
    @decorate.apimethod
    def get(self):

        return self.force_response("received")
