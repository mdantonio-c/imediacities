# -*- coding: utf-8 -*-

"""
An endpoint example
"""

import os
from commons.logs import get_logger
from ..base import ExtendedApiResource
from .. import decorators as decorate
from ...auth import authentication
from commons import htmlcodes as hcodes
# from flask_restful import request
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
    @decorate.add_endpoint_parameter('flowChunkNumber')
    @decorate.add_endpoint_parameter('flowTotalChunks')
    @decorate.apimethod
    def post(self):

        # params = self.get_input()
        chunk_number = self.get_input(single_parameter='flowChunkNumber')
        chunk_total = self.get_input(single_parameter='flowTotalChunks')
        filename = self.get_input(single_parameter='flowFilename')
        abs_fname = os.path.join("/uploads", filename)

        with open(abs_fname, "a") as f:
            f.write(".")

        if chunk_number == chunk_total:

            self.graph = self.global_get_service('neo4j')
            properties = {}
            properties["filename"] = filename
            properties["title"] = filename
            video = self.graph.createNode(self.graph.Video, properties)
            user = self.get_current_user()
            try:
                user_node = self.graph.User.nodes.get(email=user.email)
                video.ownership.connect(user_node)
            except self.graph.User.DoesNotExist:
                user_node = None

            return self.force_response(video.uuid)

        return self.force_response("", code=hcodes.HTTP_OK_ACCEPTED)
