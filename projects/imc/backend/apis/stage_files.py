# -*- coding: utf-8 -*-

"""
List content from upload dir and import of data and metadata
"""
import os
from utilities.logs import get_logger
from restapi import decorators as decorate
from restapi.services.neo4j.graph_endpoints import GraphBaseOperations
from restapi.exceptions import RestApiException
from restapi.services.neo4j.graph_endpoints import catch_graph_exceptions
# from restapi.services.mail import send_mail
from utilities import htmlcodes as hcodes

from restapi.flask_ext.flask_celery import CeleryExt

log = get_logger(__name__)


#####################################
class Stage(GraphBaseOperations):

    allowed_import_mode = ('clean', 'fast', 'skip')

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

    def lookup_content(self, path, source_id):
        '''
        Look for a filename in the form of:
        ARCHIVE_SOURCEID.[extension]
        '''
        content_filename = None
        files = [f for f in os.listdir(path) if not f.endswith('.xml')]
        for f in files:
            tokens = os.path.splitext(f)[0].split('_')
            if len(tokens) == 0:
                continue
            if tokens[-1] == source_id:
                log.info('Content file FOUND: {0}'.format(f))
                # content_path = os.path.join(path, f)
                content_filename = f
                break
        return content_filename

    @decorate.catch_error()
    @catch_graph_exceptions
    def get(self, group=None):

        self.graph = self.get_service_instance('neo4j')

        # body = "Test"
        # subject = "IMC test"
        # send_mail(body, subject)

        if not self.auth.verify_admin():
            # Only admins can specify a different group to be inspected
            group = None

        if group is None:
            group = self.getSingleLinkedNode(self.get_current_user().belongs_to)
        else:
            group = self.graph.Group.nodes.get_or_none(uuid=group)
            # group = self.getNode(self.graph.Group, group, field='uuid')

        if group is None:
            raise RestApiException(
                "No group defined for this user",
                status_code=hcodes.HTTP_BAD_REQUEST)

        upload_dir = os.path.join("/uploads", group.uuid)
        if not os.path.exists(upload_dir):
            os.mkdir(upload_dir)
            if not os.path.exists(upload_dir):
                return self.force_response(
                    [], errors=["Upload dir not found"])

        # resources = group.stage_files.all()

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

            res = self.graph.Stage.nodes.get_or_none(filename=f)
            if res is not None:
                row['status'] = res.status
                row['status_message'] = res.status_message
                row['task_id'] = res.task_id
                row['warnings'] = res.warnings
                # cast down to Meta or Content stage
                subres = res.downcast()
                if 'MetaStage' in subres.labels():
                    item = subres.item.single()
                    # add binding info ONLY for processed record
                    if item is not None:
                        binding = {}
                        source_id = None
                        creation = item.creation.single()
                        if creation is not None:
                            sources = creation.record_sources.all()
                            source_id = sources[0].source_id
                            binding['source_id'] = source_id
                        content_stage = item.content_source.single()
                        if content_stage is not None:
                            binding['filename'] = content_stage.filename
                            binding['status'] = content_stage.status
                        else:
                            binding['filename'] = self.lookup_content(upload_dir, source_id)
                            binding['status'] = 'PENDING'
                        row['binding'] = binding

            # for res in resources:
            #     if res.path != path:
            #         continue
            #     row['status'] = res.status
            #     row['status_message'] = res.status_message
            #     row['task_id'] = res.task_id
            data.append(row)

        return self.force_response(data)

    @decorate.catch_error()
    @catch_graph_exceptions
    def post(self):

        self.graph = self.get_service_instance('neo4j')

        group = self.getSingleLinkedNode(self.get_current_user().belongs_to)

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
        mode = input_parameters.get('mode', 'clean').strip().lower()
        if mode not in self.__class__.allowed_import_mode:
            raise RestApiException(
                "Bad mode parameter: expected one of %s" %
                (self.__class__.allowed_import_mode, ),
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
            resource = self.graph.MetaStage.nodes.get(**properties)
            # if ContentStage exists and status is COMPLETED
            #  then mode=skip
            if resource is not None:
                log.debug("Resource already exists for %s" % path)
                item = resource.item.single()
                if item is not None:
                    content_stage = item.content_source.single()
                    if content_stage is not None and content_stage.status == 'COMPLETED':
                        log.debug("Content resource already exists with status: " + content_stage.status + ", then mode=skip")
                        mode='skip'

        except self.graph.MetaStage.DoesNotExist:
            resource = self.graph.MetaStage(**properties).save()
            resource.ownership.connect(group)
            log.debug("Metadata Resource created for %s" % path)

        task = CeleryExt.import_file.apply_async(
            args=[path, resource.uuid, mode],
            countdown=10
        )

        resource.status = "IMPORTING"
        resource.task_id = task.id
        resource.save()

        return self.force_response(task.id)

    @decorate.catch_error()
    @catch_graph_exceptions
    def delete(self):

        self.graph = self.get_service_instance('neo4j')

        group = self.getSingleLinkedNode(self.get_current_user().belongs_to)

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
