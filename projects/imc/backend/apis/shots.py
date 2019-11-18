# -*- coding: utf-8 -*-

"""
Handle your video metadata
"""
from flask import send_file
from flask import request
from restapi.confs import get_api_url
from restapi.confs import PRODUCTION
from restapi.utilities.logs import get_logger
from restapi import decorators as decorate
from restapi.protocols.bearer import authentication
from restapi.services.neo4j.graph_endpoints import GraphBaseOperations
from restapi.exceptions import RestApiException

# from restapi.services.neo4j.graph_endpoints import graph_transactions
from restapi.services.neo4j.graph_endpoints import catch_graph_exceptions
from restapi.utilities.htmlcodes import hcodes

logger = get_logger(__name__)


#####################################
class Shots(GraphBaseOperations):

    # schema_expose = True
    labels = ['shot']
    GET = {'/shots/<shot_id>': {'summary': 'Gets information about a shot', 'description': 'Returns a single shot for its id', 'parameters': [{'name': 'content', 'in': 'query', 'description': 'content type (ONLY thumbnail at the moment)', 'type': 'string'}], 'responses': {'200': {'description': 'Shot information successfully retrieved'}, '401': {'description': 'This endpoint requires a valid authorization token'}, '404': {'description': 'The video does not exists.'}}}}

    @decorate.catch_error()
    @catch_graph_exceptions
    def get(self, shot_id=None):
        """
        Get shot by id.
        """
        logger.debug("getting Shot id: %s", shot_id)
        if shot_id is None:
            raise RestApiException(
                "Please specify a valid shot uuid", status_code=hcodes.HTTP_BAD_NOTFOUND
            )
        self.graph = self.get_service_instance('neo4j')

        input_parameters = self.get_input()
        content_type = input_parameters['content']
        if content_type is not None and content_type != 'thumbnail':
            raise RestApiException(
                "Bad type parameter: expected 'thumbnail'",
                status_code=hcodes.HTTP_BAD_REQUEST,
            )

        # check if the shot exists
        node = None
        try:
            node = self.graph.Shot.nodes.get(uuid=shot_id)
        except self.graph.Shot.DoesNotExist:
            logger.debug("Shot with id %s does not exist" % shot_id)
            raise RestApiException(
                "Please specify a valid shot id", status_code=hcodes.HTTP_BAD_NOTFOUND
            )

        if content_type is not None:
            thumbnail_uri = node.thumbnail_uri
            logger.debug("thumbnail content uri: %s" % thumbnail_uri)
            if thumbnail_uri is None:
                raise RestApiException(
                    "Thumbnail not found", status_code=hcodes.HTTP_BAD_NOTFOUND
                )
            return send_file(thumbnail_uri, mimetype='image/jpeg')

        api_url = get_api_url(request, PRODUCTION)
        shot = self.getJsonResponse(node)
        shot['links']['self'] = api_url + 'api/shots/' + node.uuid
        shot['links']['thumbnail'] = (
            api_url + 'api/shots/' + node.uuid + '?content=thumbnail'
        )

        return self.force_response(shot)


class ShotAnnotations(GraphBaseOperations):
    """
        Get all shot annotations for a given shot.
    """

    # schema_expose = True
    labels = ['shot_annotations']
    GET = {'/shots/<shot_id>/annotations': {'summary': 'Gets shot annotations.', 'description': 'Returns all the annotations targeting the given shot.', 'parameters': [{'name': 'type', 'in': 'query', 'description': 'Filter by annotation type (e.g. TAG)', 'type': 'string', 'enum': ['TAG', 'DSC']}], 'responses': {'200': {'description': 'List of annotations.'}, '401': {'description': 'This endpoint requires a valid authorzation token.'}, '404': {'description': 'Shot does not exist.'}}}}

    @decorate.catch_error()
    @catch_graph_exceptions
    @authentication.required()
    def get(self, shot_id):
        logger.info("get annotations for Shot id: %s", shot_id)
        if shot_id is None:
            raise RestApiException(
                "Please specify a shot id", status_code=hcodes.HTTP_BAD_REQUEST
            )

        params = self.get_input()
        logger.debug("inputs %s" % params)
        anno_type = params.get('type')
        if anno_type is not None:
            anno_type = anno_type.upper()

        self.graph = self.get_service_instance('neo4j')
        data = []

        shot = None
        try:
            shot = self.graph.Shot.nodes.get(uuid=shot_id)
        except self.graph.AVEntity.DoesNotExist:
            logger.debug("Shot with uuid %s does not exist" % shot_id)
            raise RestApiException(
                "Please specify a valid shot id", status_code=hcodes.HTTP_BAD_NOTFOUND
            )

        user = self.get_current_user()

        for a in shot.annotation:
            if anno_type is not None and a.annotation_type != anno_type:
                continue
            if a.private:
                if a.creator is None:
                    logger.warn(
                        'Invalid state: missing creator for private '
                        'note [UUID:{}]'.format(a.uuid)
                    )
                    continue
                creator = a.creator.single()
                if creator.uuid != user.uuid:
                    continue
            res = self.getJsonResponse(a, max_relationship_depth=0)
            del res['links']
            if a.annotation_type in ('TAG', 'DSC') and a.creator is not None:
                res['creator'] = self.getJsonResponse(
                    a.creator.single(), max_relationship_depth=0
                )
            # attach bodies
            res['bodies'] = []
            for b in a.bodies.all():
                anno_body = b.downcast()
                body = self.getJsonResponse(anno_body, max_relationship_depth=0)
                if 'links' in body:
                    del body['links']
                res['bodies'].append(body)
            data.append(res)

        return self.force_response(data)
