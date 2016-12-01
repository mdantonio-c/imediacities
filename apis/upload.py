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
from flask_restful import request
from werkzeug import secure_filename
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

        self.graph = self.global_get_service('neo4j')
        user = self.get_current_user()
        try:
            user_node = self.graph.User.nodes.get(email=user.email)
        except self.graph.User.DoesNotExist:
            user_node = None

        # params = self.get_input()
        chunk_number = self.get_input(single_parameter='flowChunkNumber')
        chunk_total = self.get_input(single_parameter='flowTotalChunks')
        filename = self.get_input(single_parameter='flowFilename')
        sec_filename = secure_filename(filename)
        root_dir = os.path.join("/uploads", user_node.uuid)
        abs_fname = os.path.join(root_dir, sec_filename)

        if not os.path.exists(root_dir):
            os.mkdir(root_dir)

        if chunk_number == "1":
            if os.path.exists(abs_fname):
                os.remove(abs_fname)

        with open(abs_fname, "ab") as f:
            request.files['file'].save(f)
            f.close()

        if chunk_number == chunk_total:

            properties = {}
            properties["filename"] = sec_filename
            properties["title"] = filename
            video = self.graph.createNode(self.graph.Video, properties)
            if user_node is not None:
                video.ownership.connect(user_node)

            return self.force_response(video.uuid)

        return self.force_response("", code=hcodes.HTTP_OK_ACCEPTED)
