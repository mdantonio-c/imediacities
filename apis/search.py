# -*- coding: utf-8 -*-

"""
Search endpoint

@author: Giuseppe Trotta <g.trotta@cineca.it>
"""
from flask import request

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

        # Retrieve the JSON data from the Request and store it in local
        # variable
        jsonData = request.get_json()
        # logger.critical(jsonData)
        # attr = {}
        # # Iterate over the JSON Data and print the data on console
        # for key in jsonData:
        #     attr[key] = jsonData[key]
        #     logger.debug("%s = %s" % (key, jsonData[key]))

        input_parameters = self.get_input()
        logger.critical(input_parameters)

        # if attr['term']:
        #     videos = self.graph.AVEntity.nodes.filter(
        #         identifying_title__icontains=attr['term'])
        # else:
        #     videos = self.graph.AVEntity.nodes.all()

        # for v in videos:
        #     video = self.getJsonResponse(v)
        #     data.append(video)

        return self.force_response(data)
