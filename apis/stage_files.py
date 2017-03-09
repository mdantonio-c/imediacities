# -*- coding: utf-8 -*-

"""
List content from upload dir and import of data and metadata
"""
import os
from commons.logs import get_logger
from .. import decorators as decorate
from ..services.neo4j.graph_endpoints import GraphBaseOperations
from ..services.neo4j.graph_endpoints import returnError
from ..services.neo4j.graph_endpoints import catch_graph_exceptions
from commons.tasks.custom.imc_tasks import import_file
from commons import htmlcodes as hcodes

log = get_logger(__name__)


#####################################
class Stage(GraphBaseOperations):

    def getType(self, filename):
        name, file_extension = os.path.splitext(filename)

        if file_extension is None:
            return "unknown"

        metadata_exts = ['.xml', '.xls']
        if file_extension in metadata_exts:
            return "metadata"

        video_exts = ['.mp4', '.ts', '.mpg', '.mpeg', '.mkv']
        if file_extension in video_exts:
            return "video"

        audio_exts = ['.aac', '.mp2', '.mp3', '.wav']
        if file_extension in audio_exts:
            return "audio"

        image_exts = ['.tif', '.jpg', '.tiff', '.jpeg']
        if file_extension in image_exts:
            return "image"

        text_exts = ['.pdf', '.doc', '.docx']
        if file_extension in text_exts:
            return "text"

        return "unknown"

    @decorate.catch_error(
        exception=Exception, exception_label=None, catch_generic=False)
    @catch_graph_exceptions
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

        resources = group.stage_files.all()

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
            row['status'] = "-"

            for res in resources:
                if res.path != path:
                    continue
                row['status'] = res.status
                row['status_message'] = res.status_message
                row['task_id'] = res.task_id
            data.append(row)

        return self.force_response(data)

    @decorate.catch_error(
        exception=Exception, exception_label=None, catch_generic=False)
    @catch_graph_exceptions
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

        properties = {}
        properties['filename'] = filename
        properties['path'] = path

        try:
            resource = self.graph.Stage.nodes.get(**properties)
            log.debug("Resource already exist for %s" % path)
        except self.graph.Stage.DoesNotExist:
            resource = self.graph.Stage(**properties).save()
            resource.ownership.connect(group)
            log.debug("Resource created for %s" % path)

        task = import_file.apply_async(
            args=[path, resource.uuid],
            countdown=20
        )

        resource.status = "IMPORTING"
        resource.task_id = task.id
        resource.save()

        return self.force_response(task.id)

    @decorate.catch_error(
        exception=Exception, exception_label=None, catch_generic=False)
    @catch_graph_exceptions
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
