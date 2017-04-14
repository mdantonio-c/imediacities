# -*- coding: utf-8 -*-

"""
Upload a file
"""

import os
from flask_restful import request

from rapydo import decorators as decorate
from rapydo.utils.logs import get_logger
from rapydo.utils import htmlcodes as hcodes
from rapydo.services.uploader import Uploader
from rapydo.services.neo4j.graph_endpoints import GraphBaseOperations
from rapydo.services.neo4j.graph_endpoints import returnError
from rapydo.services.neo4j.graph_endpoints import graph_transactions
from rapydo.services.neo4j.graph_endpoints import catch_graph_exceptions

logger = get_logger(__name__)


#####################################
class Upload(Uploader, GraphBaseOperations):

    @decorate.catch_error(exception=Exception, catch_generic=False)
    @catch_graph_exceptions
    @graph_transactions
    def post(self):

        self.initGraph()

        group = self.getSingleLinkedNode(self._current_user.belongs_to)

        if group is None:
            return returnError(
                self,
                label="Invalid request",
                error="No group defined for this user",
                code=hcodes.HTTP_BAD_REQUEST)

        upload_dir = os.path.join("/uploads", group.uuid)
        if not os.path.exists(upload_dir):
            os.mkdir(upload_dir)

        chunk_number = int(self.get_input(single_parameter='flowChunkNumber'))
        chunk_total = int(self.get_input(single_parameter='flowTotalChunks'))
        chunk_size = int(self.get_input(single_parameter='flowChunkSize'))
        filename = self.get_input(single_parameter='flowFilename')

        abs_fname, secure_name = self.ngflow_upload(
            filename, upload_dir, request.files['file'],
            chunk_number, chunk_size, chunk_total,
            overwrite=True
        )

# TO FIX: upload should creare a temporary file and only at the end rename to the real name? 
        # if chunk_number == chunk_total:

        #     properties = {}
        #     properties["filename"] = secure_name
        #     properties["title"] = filename
        #     video = self.graph.Video(**properties).save()
        #     if self._current_user is not None:
        #         video.ownership.connect(self._current_user)

        #     return self.force_response(video.uuid)

        return self.force_response("", code=hcodes.HTTP_OK_ACCEPTED)
