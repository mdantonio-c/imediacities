# -*- coding: utf-8 -*-

"""
An endpoint example
"""

from rapydo.utils.logs import get_logger
from rapydo import decorators as decorate
from rapydo.services.neo4j.graph_endpoints import GraphBaseOperations
from rapydo.services.neo4j.graph_endpoints import catch_graph_exceptions

logger = get_logger(__name__)


#####################################
class Search(GraphBaseOperations):

    @decorate.catch_error()
    @catch_graph_exceptions
    def post(self, term=None):

        self.initGraph()
        data = []

        if term is not None:
            v = self.graph.AVEntity.nodes.get(
                identifying_title__contains=term)
            videos = [v]
        else:
            videos = self.graph.AVEntity.nodes.all()

        for v in videos:

            video = {}
            video["title"] = v.identifying_title
            video["description"] = ''
            video["production_years"] = v.production_years
            data.append(video)

        return self.force_response(data)
