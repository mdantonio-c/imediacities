# -*- coding: utf-8 -*-

"""
Handle your image entity
"""
from flask import request, send_file
from utilities.helpers import get_api_url
from restapi.confs import PRODUCTION

from utilities.logs import get_logger
from imc.security import authz
from restapi import decorators as decorate
from restapi.services.neo4j.graph_endpoints import GraphBaseOperations
from restapi.services.download import Downloader
from restapi.exceptions import RestApiException
from restapi.services.neo4j.graph_endpoints import graph_transactions
from restapi.services.neo4j.graph_endpoints import catch_graph_exceptions
from utilities import htmlcodes as hcodes
from imc.tasks.services.creation_repository import CreationRepository
from imc.tasks.services.annotation_repository import AnnotationRepository

from restapi.flask_ext.flask_celery import CeleryExt

logger = get_logger(__name__)


#####################################
class Images(GraphBaseOperations):

    """
    Get an NonAVEntity if its id is passed as an argument.
    Else return all NonAVEntities in the repository.
    """
    @decorate.catch_error()
    @catch_graph_exceptions
    def get(self, image_id=None):
        logger.debug("getting NonAVEntity id: %s", image_id)
        self.graph = self.get_service_instance('neo4j')
        data = []

        if image_id is not None:
            # check if the image exists
            try:
                v = self.graph.NonAVEntity.nodes.get(uuid=image_id)
            except self.graph.NonAVEntity.DoesNotExist:
                logger.debug(
                    "NonAVEntity with uuid %s does not exist" % image_id)
                raise RestApiException(
                    "Please specify a valid image id",
                    status_code=hcodes.HTTP_BAD_NOTFOUND)
            images = [v]
        else:
            images = self.graph.NonAVEntity.nodes.all()

        api_url = get_api_url(request, PRODUCTION)
        for v in images:
            image = self.getJsonResponse(
                v, max_relationship_depth=1,
                relationships_expansion=[
                    'record_sources.provider',
                    'item.ownership'
                ]
            )
            item = v.item.single()
            # image['links']['self'] = api_url + \
            #     'api/images/' + v.uuid
            image['links']['content'] = api_url + \
                'api/images/' + v.uuid + '/content?type=image'
            if item.thumbnail is not None:
                image['links']['thumbnail'] = api_url + \
                    'api/images/' + v.uuid + '/content?type=thumbnail'
            image['links']['summary'] = api_url + \
                'api/images/' + v.uuid + '/content?type=summary'
            data.append(image)

        return self.force_response(data)

    """
    Create a new image description.
    """
    @decorate.catch_error()
    @catch_graph_exceptions
    @graph_transactions
    def post(self):
        self.graph = self.get_service_instance('neo4j')

        v = self.get_input()
        if len(v) == 0:
            raise RestApiException(
                'Empty input',
                status_code=hcodes.HTTP_BAD_REQUEST)

        # schema = self.get_endpoint_custom_definition()

        data = self.get_input()

        logger.critical(data)

        return self.empty_response()

    @decorate.catch_error()
    @catch_graph_exceptions
    @graph_transactions
    def delete(self, image_id):
        """
        Delete existing image description.
        """
        logger.debug("deliting NonAVEntity id: %s", image_id)
        self.graph = self.get_service_instance('neo4j')

        if image_id is None:
            raise RestApiException(
                "Please specify a valid image id",
                status_code=hcodes.HTTP_BAD_REQUEST)
        try:
            v = self.graph.NonAVEntity.nodes.get(uuid=image_id)
            repo = CreationRepository(self.graph)
            repo.delete_non_av_entity(v)
            return self.empty_response()
        except self.graph.NonAVEntity.DoesNotExist:
            logger.debug("NonAVEntity with uuid %s does not exist" % image_id)
            raise RestApiException(
                "Please specify a valid image id",
                status_code=hcodes.HTTP_BAD_NOTFOUND)


class ImageItem(GraphBaseOperations):

    @decorate.catch_error()
    @catch_graph_exceptions
    @graph_transactions
    def put(self, image_id):
        """
        Allow user to update item information.
        """
        logger.debug("Update Item for NonAVEntity uuid: %s", image_id)
        if image_id is None:
            raise RestApiException(
                "Please specify a image id",
                status_code=hcodes.HTTP_BAD_REQUEST)
        self.graph = self.get_service_instance('neo4j')
        try:
            v = self.graph.NonAVEntity.nodes.get(uuid=image_id)
        except self.graph.NonAVEntity.DoesNotExist:
            logger.debug("NonAVEntity with uuid %s does not exist" % image_id)
            raise RestApiException(
                "Please specify a valid image id",
                status_code=hcodes.HTTP_BAD_NOTFOUND)
        item = v.item.single()
        if item is None:
            raise RestApiException(
                "This NonAVEntity may not have been correctly imported. "
                "Item info not found",
                status_code=hcodes.HTTP_BAD_NOTFOUND)

        data = self.get_input()
        # ONLY public_access allowed at the moment
        public_access = data.get('public_access')
        if public_access is None or type(public_access) != bool:
            raise RestApiException(
                "Please specify a valid value for public_access",
                status_code=hcodes.HTTP_BAD_REQUEST)

        item.public_access = public_access
        item.save()
        logger.debug("Item successfully updated for NonAVEntity uuid {}. {}"
                     .format(image_id, item))

        # 204: Item successfully updated.
        return self.empty_response()


class ImageAnnotations(GraphBaseOperations):
    """
        Get all image annotations for a given image.
    """
    @decorate.catch_error()
    @catch_graph_exceptions
    def get(self, image_id):
        logger.debug("get annotations for NonAVEntity id: %s", image_id)
        if image_id is None:
            raise RestApiException(
                "Please specify a image id",
                status_code=hcodes.HTTP_BAD_REQUEST)

        params = self.get_input()
        anno_type = params.get('type')
        if anno_type is not None:
            anno_type = anno_type.upper()

        self.graph = self.get_service_instance('neo4j')
        data = []

        image = None
        try:
            image = self.graph.NonAVEntity.nodes.get(uuid=image_id)
        except self.graph.NonAVEntity.DoesNotExist:
            logger.debug("NonAVEntity with uuid %s does not exist" % image_id)
            raise RestApiException(
                "Please specify a valid image id",
                status_code=hcodes.HTTP_BAD_NOTFOUND)

        user = self.get_current_user()

        item = image.item.single()
        for anno in item.targeting_annotations:
            if anno_type is not None and anno.annotation_type != anno_type:
                continue
            if anno.private:
                if anno.creator is None:
                    # expected ALWAYS a creator for private annotation
                    logger.warn('Invalid state: missing creator for private '
                                'anno [UUID:{}]'.format(anno.uuid))
                    continue
                creator = anno.creator.single()
                if user is None or creator.uuid != user.uuid:
                        continue
            res = self.getJsonResponse(anno, max_relationship_depth=0)
            del(res['links'])
            if anno.annotation_type in ('TAG', 'DSC', 'LNK') and anno.creator is not None:
                res['creator'] = self.getJsonResponse(
                    anno.creator.single(), max_relationship_depth=0)
            # attach bodies
            res['bodies'] = []
            for b in anno.bodies.all():
                mdb = b.downcast()
                if anno.annotation_type == 'TAG' and 'ODBody' in mdb.labels():
                    # object detection body
                    body = self.getJsonResponse(
                        mdb.object_type.single(), max_relationship_depth=0)
                else:
                    body = self.getJsonResponse(
                        mdb, max_relationship_depth=0)
                if 'links' in body:
                    del(body['links'])
                res['bodies'].append(body)
            data.append(res)

        return self.force_response(data)


class ImageContent(GraphBaseOperations):
    """
    Gets image content or thumbnail
    """
    @decorate.catch_error()
    @catch_graph_exceptions
    @authz.pre_authorize
    def get(self, image_id):
        logger.info("get image content for id %s" % image_id)
        if image_id is None:
            raise RestApiException(
                "Please specify a image id",
                status_code=hcodes.HTTP_BAD_REQUEST)

        input_parameters = self.get_input()
        content_type = input_parameters['type']
        if content_type is None or (content_type != 'image' and
                                    content_type != 'thumbnail'):
            raise RestApiException(
                "Bad type parameter: expected 'image' or 'thumbnail'",
                status_code=hcodes.HTTP_BAD_REQUEST)

        self.graph = self.get_service_instance('neo4j')
        image = None
        try:
            image = self.graph.NonAVEntity.nodes.get(uuid=image_id)
        except self.graph.NonAVEntity.DoesNotExist:
            logger.debug("NonAVEntity with uuid %s does not exist" % image_id)
            raise RestApiException(
                "Please specify a valid image id",
                status_code=hcodes.HTTP_BAD_NOTFOUND)

        item = image.item.single()
        logger.debug("item data: " + format(item))
        if content_type == 'image':
            # TODO manage here content access (see issue 190)
            # always return the other version if available
            image_uri = item.uri
            other_version = item.other_version.single()
            if other_version is not None:
                image_uri = other_version.uri
            logger.debug("image content uri: %s" % image_uri)
            if image_uri is None:
                raise RestApiException(
                    "Image not found",
                    status_code=hcodes.HTTP_BAD_NOTFOUND)
            # image is always jpeg
            mime = "image/jpeg"
            download = Downloader()
            return download.send_file_partial(image_uri, mime)
        elif content_type == 'thumbnail':
            thumbnail_uri = item.thumbnail
            logger.debug("thumbnail content uri: %s" % thumbnail_uri)
            thumbnail_size = input_parameters.get('size')
            if thumbnail_size is not None and thumbnail_size.lower() == 'large':
                # load large image file as the original (i.e. transcoded.jpg)
                thumbnail_uri = item.uri
                logger.debug(
                    'request for large thumbnail: {}'.format(thumbnail_uri))
            if thumbnail_uri is None:
                raise RestApiException(
                    "Thumbnail not found",
                    status_code=hcodes.HTTP_BAD_NOTFOUND)
            return send_file(thumbnail_uri, mimetype='image/jpeg')
        else:
            # it should never be reached
            raise RestApiException(
                "Invalid content type: {0}".format(content_type),
                status_code=hcodes.HTTP_NOT_IMPLEMENTED)


class ImageTools(GraphBaseOperations):

    __available_tools__ = ('object-detection', 'building-recognition')

    @decorate.catch_error()
    @catch_graph_exceptions
    def post(self, image_id):

        logger.debug('launch automatic tool for image id: %s' % image_id)

        if image_id is None:
            raise RestApiException(
                "Please specify a image id",
                status_code=hcodes.HTTP_BAD_REQUEST)

        self.graph = self.get_service_instance('neo4j')
        image = None
        try:
            image = self.graph.NonAVEntity.nodes.get(uuid=image_id)
        except self.graph.NonAVEntity.DoesNotExist:
            logger.debug("NonAVEntity with uuid %s does not exist" % image_id)
            raise RestApiException(
                "Please specify a valid image id.",
                status_code=hcodes.HTTP_BAD_NOTFOUND)
        item = image.item.single()
        if item is None:
            raise RestApiException(
                "Item not available. Execute the pipeline first!",
                status_code=hcodes.HTTP_BAD_CONFLICT)
        if item.item_type != 'Image':
            raise RestApiException(
                "Content item is not a image. Use a valid image id.",
                status_code=hcodes.HTTP_BAD_REQUEST)

        params = self.get_input()
        if 'tool' not in params:
            raise RestApiException(
                'Please specify the tool to be launched.',
                status_code=hcodes.HTTP_BAD_REQUEST)
        tool = params['tool']
        if tool not in self.__available_tools__:
            raise RestApiException(
                "Please specify a valid tool. Expected one of %s." %
                (self.__available_tools__, ),
                status_code=hcodes.HTTP_BAD_REQUEST)

        repo = AnnotationRepository(self.graph)
        if tool == self.__available_tools__[0]:  # object-detection
            if ('operation' in params and params['operation'] == 'delete'):
                # get all automatic object detection tags
                deleted = 0
                for anno in item.sourcing_annotations.search(annotation_type='TAG', generator='FHG'):
                    # expected always single body for automatic tags
                    body = anno.bodies.single()
                    if 'ODBody' in body.labels() and 'BRBody' not in body.labels():
                        deleted += 1
                        repo.delete_auto_annotation(anno)
                return self.force_response(
                    "There are no more automatic object detection tags for image {}. Deleted {}".format(
                        image_id, deleted),
                    code=hcodes.HTTP_OK_BASIC)
            # DO NOT re-import object detection twice for the same image!
            if repo.check_automatic_od(item.uuid):
                raise RestApiException(
                    "Object detection CANNOT be import twice for the same image.",
                    status_code=hcodes.HTTP_BAD_CONFLICT)
        elif tool == self.__available_tools__[1]:  # building-recognition
            if ('operation' in params and params['operation'] == 'delete'):
                # get all automatic building recognition tags
                deleted = 0
                for anno in item.sourcing_annotations.search(annotation_type='TAG', generator='FHG'):
                    # expected always single body for automatic tags
                    body = anno.bodies.single()
                    if 'BRBody' in body.labels():
                        deleted += 1
                        repo.delete_auto_annotation(anno)
                return self.force_response(
                    "There are no more automatic building recognition tags for image {}. Deleted {}".format(
                        image_id, deleted),
                    code=hcodes.HTTP_OK_BASIC)
            # DO NOT re-import building recognition twice for the same image!
            if repo.check_automatic_br(item.uuid):
                raise RestApiException(
                    "Building recognition CANNOT be import twice for the same image.",
                    status_code=hcodes.HTTP_BAD_CONFLICT)
        else:
            # should never be reached
            raise RestApiException(
                "Specified tool '{}' NOT implemented".format(tool),
                status_code=hcodes.HTTP_NOT_IMPLEMENTED)

        task = CeleryExt.launch_tool.apply_async(
            args=[tool, item.uuid],
            countdown=10
        )

        return self.force_response(task.id, code=hcodes.HTTP_OK_ACCEPTED)
