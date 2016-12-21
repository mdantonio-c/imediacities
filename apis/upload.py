# -*- coding: utf-8 -*-

"""
Upload a file
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
from ..services.neo4j.graph_endpoints import returnError
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
    @authentication.authorization_required(roles=['Archive'])
    @decorate.add_endpoint_parameter('flowFilename')
    @decorate.add_endpoint_parameter('flowChunkNumber')
    @decorate.add_endpoint_parameter('flowTotalChunks')
    @decorate.add_endpoint_parameter('flowChunkSize')
    @decorate.apimethod
    def post(self):

        self.initGraph()

        group = self.getSingleLinkedNode(self._current_user.belongs_to)

        if group is None:
            return returnError(
                self,
                label="Invalid request",
                error="No group defined for this user",
                code=hcodes.HTTP_BAD_REQUEST)

        root_dir = os.path.join("/uploads", group.uuid)
        if not os.path.exists(root_dir):
            os.mkdir(root_dir)

        chunk_number = int(self.get_input(single_parameter='flowChunkNumber'))
        chunk_total = int(self.get_input(single_parameter='flowTotalChunks'))
        chunk_size = int(self.get_input(single_parameter='flowChunkSize'))
        filename = self.get_input(single_parameter='flowFilename')

        abs_fname, secure_name = self.ngflow_upload(
            filename, root_dir, request.files['file'],
            chunk_number, chunk_size, chunk_total,
            overwrite=True
        )

# TO FIX: upload should creare a temporary file and only at the end rename to the real name? 
        # if chunk_number == chunk_total:

        #     properties = {}
        #     properties["filename"] = secure_name
        #     properties["title"] = filename
        #     video = self.graph.createNode(self.graph.Video, properties)
        #     if self._current_user is not None:
        #         video.ownership.connect(self._current_user)

        #     return self.force_response(video.uuid)

        return self.force_response("", code=hcodes.HTTP_OK_ACCEPTED)
