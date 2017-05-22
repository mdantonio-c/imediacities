# -*- coding: utf-8 -*-

"""
Search endpoint

@author: Giuseppe Trotta <g.trotta@cineca.it>
"""

from rapydo.confs import get_api_url

from rapydo.utils.logs import get_logger
from rapydo import decorators as decorate
from rapydo.services.neo4j.graph_endpoints import GraphBaseOperations
from rapydo.services.neo4j.graph_endpoints import catch_graph_exceptions

logger = get_logger(__name__)


#####################################
class Search(GraphBaseOperations):

    @decorate.catch_error()
    @catch_graph_exceptions
    def post(self):

        self.initGraph()
        data = []

        input_parameters = self.get_input()
        logger.debug(input_parameters)

        if input_parameters['term']:
            videos = self.graph.AVEntity.nodes.filter(
                identifying_title__icontains=input_parameters['term'])
        else:
            videos = self.graph.AVEntity.nodes.all()

        api_url = get_api_url()
        for v in videos:
            video = self.getJsonResponse(v)
            logger.info("links %s " % video['links'])
            video['links']['self'] = api_url + \
                'api/videos/' + v.uuid
            video['links']['content'] = api_url + \
                'api/videos/' + v.uuid + '/content?type=video'
            video['links']['thumbnail'] = api_url + \
                'api/videos/' + v.uuid + '/content?type=thumbnail'
            data.append(video)

        return self.force_response(data)