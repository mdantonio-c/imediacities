# -*- coding: utf-8 -*-

"""
List content from upload dir and import of data and metadata
"""
import os
from rapydo.utils.logs import get_logger
from rapydo import decorators as decorate
from rapydo.services.neo4j.graph_endpoints import GraphBaseOperations
from rapydo.exceptions import RestApiException
from rapydo.services.neo4j.graph_endpoints import catch_graph_exceptions
from rapydo.utils import htmlcodes as hcodes

from flask_ext.flask_celery import CeleryExt

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

    @decorate.catch_error()
    @catch_graph_exceptions
    def get(self, group=None):

        self.initGraph()

        if group is None:
            group = self.getSingleLinkedNode(self._current_user.belongs_to)
        else:
            group = self.getNode(self.graph.Group, group, field='uuid')

        if group is None:
            raise RestApiException(
                "No group defined for this user",
                status_code=hcodes.HTTP_BAD_REQUEST)

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

    @decorate.catch_error()
    @catch_graph_exceptions
    def post(self):

        self.initGraph()

        group = self.getSingleLinkedNode(self._current_user.belongs_to)

        if group is None:
            raise RestApiException(
                "No group defined for this user",
                status_code=hcodes.HTTP_BAD_REQUEST)

        upload_dir = os.path.join("/uploads", group.uuid)
        if not os.path.exists(upload_dir):
            raise RestApiException(
                "Upload dir not found",
                status_code=hcodes.HTTP_BAD_REQUEST)

        input_parameters = self.get_input()

        if 'filename' not in input_parameters:
            raise RestApiException(
                "Filename not found",
                status_code=hcodes.HTTP_BAD_REQUEST)

        filename = input_parameters['filename']
        mode = input_parameters['mode']
        if mode is not None and mode != 'clean' and mode != 'fast':
            raise RestApiException(
                "Bad mode parameter: expected 'fast' or 'clean'",
                status_code=hcodes.HTTP_BAD_REQUEST)

        path = os.path.join(upload_dir, filename)
        if not os.path.isfile(path):
            raise RestApiException(
                "File not found: %s" % filename,
                status_code=hcodes.HTTP_BAD_REQUEST)

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

        task = CeleryExt.import_file.apply_async(
            args=[path, resource.uuid, mode],
            countdown=20
        )

        resource.status = "IMPORTING"
        resource.task_id = task.id
        resource.save()

        return self.force_response(task.id)

    @decorate.catch_error()
    @catch_graph_exceptions
    def delete(self):

        self.initGraph()

        group = self.getSingleLinkedNode(self._current_user.belongs_to)

        if group is None:
            raise RestApiException(
                "No group defined for this user",
                status_code=hcodes.HTTP_BAD_REQUEST)

        upload_dir = os.path.join("/uploads", group.uuid)
        if not os.path.exists(upload_dir):
            raise RestApiException(
                "Upload dir not found",
                status_code=hcodes.HTTP_BAD_REQUEST)

        input_parameters = self.get_input()

        if 'filename' not in input_parameters:
            raise RestApiException(
                "Filename not found",
                status_code=hcodes.HTTP_BAD_REQUEST)

        filename = input_parameters['filename']

        path = os.path.join(upload_dir, filename)
        if not os.path.isfile(path):
            raise RestApiException(
                "File not found: %s" % filename,
                status_code=hcodes.HTTP_BAD_REQUEST)

        os.remove(path)
        return self.empty_response()
