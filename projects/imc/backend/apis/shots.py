# -*- coding: utf-8 -*-

"""
Handle your video metadata
"""
from flask import send_file
from flask import request
from utilities.helpers import get_api_url
from restapi.confs import PRODUCTION

from utilities.logs import get_logger
from restapi import decorators as decorate
from restapi.services.neo4j.graph_endpoints import GraphBaseOperations
from restapi.exceptions import RestApiException
# from restapi.services.neo4j.graph_endpoints import graph_transactions
from restapi.services.neo4j.graph_endpoints import catch_graph_exceptions
from utilities import htmlcodes as hcodes

logger = get_logger(__name__)


#####################################
class Shots(GraphBaseOperations):

    @decorate.catch_error()
    @catch_graph_exceptions
    def get(self, shot_id=None):
        """
        Get shot by id.
        """
        logger.debug("getting Shot id: %s", shot_id)
        if shot_id is None:
            raise RestApiException(
                "Please specify a valid shot uuid",
                status_code=hcodes.HTTP_BAD_NOTFOUND)
        self.graph = self.get_service_instance('neo4j')

        input_parameters = self.get_input()
        content_type = input_parameters['content']
        if content_type is not None and content_type != 'thumbnail':
            raise RestApiException(
                "Bad type parameter: expected 'thumbnail'",
                status_code=hcodes.HTTP_BAD_REQUEST)

        # check if the shot exists
        node = None
        try:
            node = self.graph.Shot.nodes.get(uuid=shot_id)
        except self.graph.Shot.DoesNotExist:
            logger.debug("Shot with id %s does not exist" % shot_id)
            raise RestApiException(
                "Please specify a valid shot id",
                status_code=hcodes.HTTP_BAD_NOTFOUND)

        if content_type is not None:
            thumbnail_uri = node.thumbnail_uri
            logger.debug("thumbnail content uri: %s" % thumbnail_uri)
            if thumbnail_uri is None:
                raise RestApiException(
                    "Thumbnail not found",
                    status_code=hcodes.HTTP_BAD_NOTFOUND)
            return send_file(thumbnail_uri, mimetype='image/jpeg')

        api_url = get_api_url(request, PRODUCTION)
        shot = self.getJsonResponse(node)
        shot['links']['self'] = api_url + \
            'api/shots/' + node.uuid
        shot['links']['thumbnail'] = api_url + \
            'api/shots/' + node.uuid + '?content=thumbnail'

        return self.force_response(shot)
