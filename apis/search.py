# -*- coding: utf-8 -*-

"""
An endpoint example
"""

from commons.logs import get_logger
from .. import decorators as decorate
from ..services.neo4j.graph_endpoints import GraphBaseOperations
from ..services.neo4j.graph_endpoints import catch_graph_exceptions

logger = get_logger(__name__)


#####################################
class Search(GraphBaseOperations):

    @decorate.catch_error(
        exception=Exception, exception_label=None, catch_generic=False)
    @catch_graph_exceptions
    def post(self, video_id=None):

        self.initGraph()
        data = []

        if video_id is not None:
            v = self.graph.Video.nodes.get(id=video_id)
            videos = [v]
        else:
            videos = self.graph.Video.nodes.all()

        for v in videos:

            video = {}
            video["title"] = v.title
            video["description"] = v.description
            video["duration"] = v.duration
            data.append(video)

        return self.force_response(data)
