# -*- coding: utf-8 -*-

"""
Handle your iamge metadata
"""
from flask import request, send_file
from utilities.helpers import get_api_url
from restapi.confs import PRODUCTION

from utilities.logs import get_logger
from restapi import decorators as decorate
from restapi.services.neo4j.graph_endpoints import GraphBaseOperations
from restapi.services.download import Downloader
from restapi.exceptions import RestApiException
from restapi.services.neo4j.graph_endpoints import graph_transactions
from restapi.services.neo4j.graph_endpoints import catch_graph_exceptions
from utilities import htmlcodes as hcodes
from imc.tasks.services.creation_repository import CreationRepository

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
                logger.debug("NonAVEntity with uuid %s does not exist" % image_id)
                raise RestApiException(
                    "Please specify a valid image id",
                    status_code=hcodes.HTTP_BAD_NOTFOUND)
            images = [v]
        else:
            images = self.graph.NonAVEntity.nodes.all()

        api_url = get_api_url(request, PRODUCTION)
        for v in images:
            # use depth 2 to get provider info from record source
            # TO BE FIXED
            image = self.getJsonResponse(v, max_relationship_depth=2)
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


class ImageAnnotations(GraphBaseOperations):
    """
        Get all image annotations for a given image.
    """
    @decorate.catch_error()
    @catch_graph_exceptions
    def get(self, image_id):
        logger.info("get annotations for NonAVEntity id: %s", image_id)
        if image_id is None:
            raise RestApiException(
                "Please specify a image id",
                status_code=hcodes.HTTP_BAD_REQUEST)

        params = self.get_input()
        logger.debug("inputs %s" % params)
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
        for a in item.targeting_annotations:
            if anno_type is not None and a.annotation_type != anno_type:
                continue
            if a.private:
                if a.creator is None:
                    logger.warn('Invalid state: missing creator for private '
                                'note [UUID:{}]'.format(a.uuid))
                    continue
                creator = a.creator.single()
                if creator.uuid != user.uuid:
                    continue
            res = self.getJsonResponse(a, max_relationship_depth=0)
            del(res['links'])
            if a.annotation_type in ('TAG', 'DSC') and a.creator is not None:
                res['creator'] = self.getJsonResponse(
                    a.creator.single(), max_relationship_depth=0)
            # attach bodies
            res['bodies'] = []
            for b in a.bodies.all():
                anno_body = b.downcast()
                body = self.getJsonResponse(anno_body, max_relationship_depth=0)
                if 'links' in body:
                    del(body['links'])
                if a.annotation_type == 'TVS':
                    segments = []
                    for segment in anno_body.segments:
                        # look at the most derivative class
                        json_segment = self.getJsonResponse(
                            segment.downcast(), max_relationship_depth=0)
                        if 'links' in json_segment:
                            del(json_segment['links'])
                        segments.append(json_segment)
                    body['segments'] = segments
                res['bodies'] .append(body)
            data.append(res)

        return self.force_response(data)


class ImageContent(GraphBaseOperations):
    """
    Gets image content or thumbnail
    """
    @decorate.catch_error()
    @catch_graph_exceptions
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
            image_uri = item.uri
            logger.debug("image content uri: %s" % image_uri)
            if image_uri is None:
                raise RestApiException(
                    "Image not found",
                    status_code=hcodes.HTTP_BAD_NOTFOUND)

            # mime = item.digital_format[2]
            # TO FIX: is it always jpeg?
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
