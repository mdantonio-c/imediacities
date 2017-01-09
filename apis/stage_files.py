# -*- coding: utf-8 -*-

"""
List content from upload dir and import of data and metadata
"""
import os
from commons.logs import get_logger
from .. import decorators as decorate
from ...auth import authentication
from ..services.neo4j.graph_endpoints import GraphBaseOperations
# from ..services.neo4j.graph_endpoints import myGraphError
from ..services.neo4j.graph_endpoints import returnError
from ..services.neo4j.graph_endpoints import catch_graph_exceptions
from commons import htmlcodes as hcodes

logger = get_logger(__name__)


#####################################
class Stage(GraphBaseOperations):

    def getType(self, filename):
        name, file_extension = os.path.splitext(filename)

        if file_extension is None:
            return "unknown"

        metadata_exts = ['xml', 'xls']
        if file_extension in metadata_exts:
            return "metadata"

        video_exts = ['mov', 'avi', 'mp4', 'wmv']
        if file_extension in video_exts:
            return "video"

        return "unknown"

    @decorate.catch_error(
        exception=Exception, exception_label=None, catch_generic=False)
    @catch_graph_exceptions
    @authentication.authorization_required
    def get(self):

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
            return self.force_response(
                [], errors=[{"Warning": "Upload dir not found"}]
            )

        data = []
        for f in os.listdir(upload_dir):
            path = os.path.join(upload_dir, f)
            if not os.path.isfile(path):
                continue
            if f[0] == '.':
                continue
            stat = os.stat(path)
            row = {}
            row['name'] = f
            row['size'] = stat.st_size
            row['creation'] = stat.st_ctime
            row['modification'] = stat.st_mtime
            row['type'] = self.getType(f)

            data.append(row)

        return self.force_response(data)

    @decorate.catch_error(
        exception=Exception, exception_label=None, catch_generic=False)
    @catch_graph_exceptions
    @authentication.authorization_required
    def delete(self):

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
            return returnError(
                self,
                label="Error",
                error="Upload dir not found",
                code=hcodes.HTTP_BAD_REQUEST)

        input_parameters = self.get_input()

        if 'filename' not in input_parameters:
            return returnError(
                self,
                label="Missing parameter",
                error="Filename not found",
                code=hcodes.HTTP_BAD_REQUEST)

        filename = input_parameters['filename']

        path = os.path.join(upload_dir, filename)
        if not os.path.isfile(path):
            return returnError(
                self,
                label="File not found",
                error="%s" % filename,
                code=hcodes.HTTP_BAD_REQUEST)

        os.remove(path)
        return self.empty_response()
