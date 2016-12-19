# -*- coding: utf-8 -*-

"""
An endpoint example
"""

import os
from commons.logs import get_logger
from .. import decorators as decorate
from ...auth import authentication
from commons import htmlcodes as hcodes
from flask_restful import request
from ..services.uploader import Uploader
from ..services.neo4j.graph_endpoints import GraphBaseOperations
# from ..services.neo4j.graph_endpoints import myGraphError
# from ..services.neo4j.graph_endpoints import returnError
from ..services.neo4j.graph_endpoints import graph_transactions
from ..services.neo4j.graph_endpoints import catch_graph_exceptions
# from commons.services.uuid import getUUID

logger = get_logger(__name__)


#####################################
class Upload(Uploader, GraphBaseOperations):

    @decorate.catch_error(
        exception=Exception, exception_label=None, catch_generic=False)
    @catch_graph_exceptions
    @graph_transactions
    @authentication.authorization_required
    @decorate.add_endpoint_parameter('flowFilename')
    @decorate.add_endpoint_parameter('flowChunkNumber')
    @decorate.add_endpoint_parameter('flowTotalChunks')
    @decorate.add_endpoint_parameter('flowChunkSize')
    @decorate.apimethod
    def post(self):

        self.initGraph()

        root_dir = os.path.join("/uploads", self._current_user.uuid)
        if not os.path.exists(root_dir):
            os.mkdir(root_dir)

        chunk_number = int(self.get_input(single_parameter='flowChunkNumber'))
        chunk_total = int(self.get_input(single_parameter='flowTotalChunks'))
        chunk_size = int(self.get_input(single_parameter='flowChunkSize'))
        filename = self.get_input(single_parameter='flowFilename')

        abs_fname = self.ngflow_upload(
            filename, root_dir, request.files['file'],
            chunk_number, chunk_size, chunk_total,
            overwrite=True
        )

# TO FIX: what happens if last chunk doesn't arrive as last?
        if chunk_number == chunk_total:

            properties = {}
            properties["filename"] = abs_fname
            properties["title"] = filename
            video = self.graph.createNode(self.graph.Video, properties)
            if self._current_user is not None:
                video.ownership.connect(self._current_user)

            return self.force_response(video.uuid)

        return self.force_response("", code=hcodes.HTTP_OK_ACCEPTED)
