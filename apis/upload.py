# -*- coding: utf-8 -*-

"""
An endpoint example
"""

import os
from commons.logs import get_logger
from ..base import ExtendedApiResource
from .. import decorators as decorate
from ...auth import authentication
# from flask_restful import request
# from commons import htmlcodes as hcodes
# from commons.services.uuid import getUUID

logger = get_logger(__name__)


#####################################
class Upload(ExtendedApiResource):

    @authentication.authorization_required
    # @decorate.add_endpoint_parameter('flowChunkSize')
    # @decorate.add_endpoint_parameter('flowCurrentChunkSize')
    # @decorate.add_endpoint_parameter('flowTotalSize')
    # @decorate.add_endpoint_parameter('flowIdentifier')
    @decorate.add_endpoint_parameter('flowFilename')
    # @decorate.add_endpoint_parameter('flowRelativePath')
    # @decorate.add_endpoint_parameter('flowTotalChunks')
    @decorate.apimethod
    def post(self):

        # params = self.get_input()
        filename = self.get_input(single_parameter='flowFilename')
        abs_fname = os.path.join("/uploads", filename)

        with open(abs_fname, "a") as f:
            f.write(".")

        return self.force_response("received")
